"""
game.train_simulator

Headless training environment scaffold and simple trainer helper for RL policies.
This module is intentionally lightweight and will warn if required dependencies
are missing. It provides a minimal OpenAI Gym-like environment wrapper around
enemy_ai.EnemyShip suitable for stable-baselines3 training with PPO/DQN.

Usage:
- pip install stable-baselines3[extra] gym numpy torch
- python scripts/train_rl.py --output models/ppo_tie

Note: The provided environment is a simplified combat simulator for initial
experiments; extend it to match the full game's observation/action space and
reward shaping.
"""
from __future__ import annotations
import time
import numpy as np
from typing import Optional

from game import enemy_ai

# Try to import gym and stable-baselines3 but fail gracefully
try:
    import gym
    from gym import spaces
    GYM_AVAILABLE = True
except Exception:
    GYM_AVAILABLE = False

try:
    from stable_baselines3 import PPO
    SB3_AVAILABLE = True
except Exception:
    SB3_AVAILABLE = False


class HeadlessCombatEnv:
    """
    Minimal gym-like env for training a single enemy ship against a scripted player.
    Observation: enemy_ai.Observation.to_vector()
    Action: discrete over enemy_ai.Action members
    """

    def __init__(self, render: bool = False):
        self.render_mode = render
        self.enemy: Optional[enemy_ai.EnemyShip] = None
        self.player = {'position': np.array([0.0, 0.0], dtype=np.float32), 'velocity': np.array([0.0, 0.0]), 'heading': 0.0}
        self.step_count = 0
        self.max_steps = 1000

        # define spaces if gym available
        if GYM_AVAILABLE:
            obs_sample = enemy_ai.Observation(1.0, (0.0, 0.0), (0.0, 0.0), 0.0, 1000.0, 1000.0, 1000.0, 1.0, 1.0)
            v = obs_sample.to_vector()
            self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=v.shape, dtype=np.float32)
            self.action_space = spaces.Discrete(len(list(enemy_ai.Action)))

    def reset(self):
        # spawn a new enemy
        self.enemy = enemy_ai.EnemyShip(enemy_ai.ShipType.TIE_FIGHTER, position=(0.0, -200.0), heading=90.0)
        self.enemy.mode = 'rl'
        self.step_count = 0
        return self._get_obs()

    def _get_obs(self):
        obs = self.enemy._observe({'player': self.player})
        return obs.to_vector()

    def step(self, action_idx: int):
        # map action idx to Action enum
        action = list(enemy_ai.Action)[action_idx]
        # execute action directly for simplicity
        # convert to one-frame update
        dt = 1.0 / 20.0
        # we call enemy._execute_action for low-level action mapping
        self.enemy._execute_action(action, dt)
        # simple scripted player: approach enemy slowly
        dir_vec = self.enemy.position - self.player['position']
        dist = np.linalg.norm(dir_vec)
        if dist > 200:
            self.player['position'] += np.array([0.0, 1.0]) * 20.0 * dt
        # compute reward: encourage approaching and survival
        reward = 0.0
        # positive reward for getting closer to player (simulates attacking)
        new_dist = np.linalg.norm(self.enemy.position - self.player['position'])
        reward += max(0.0, (dist - new_dist) * 0.01)
        # small penalty for time to encourage faster behavior
        reward -= 0.001

        self.step_count += 1
        done = self.step_count >= self.max_steps
        info = {}
        return self._get_obs(), float(reward), done, info

    # gym API compatibility
    def render(self, mode='human'):
        if self.render_mode:
            print(f"Enemy pos: {self.enemy.position}")


def train_default(output_path: str, timesteps: int = 10000):
    if not GYM_AVAILABLE or not SB3_AVAILABLE:
        raise RuntimeError("Required dependencies missing. Install gym and stable-baselines3 to train.")
    env = gym.make('CartPole-v1')  # placeholder; replace with proper gym wrapper below
    # If desired: create a gym.Env wrapper around HeadlessCombatEnv
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=timesteps)
    model.save(output_path)


if __name__ == '__main__':
    print('This module provides HeadlessCombatEnv and a train_default helper.')
