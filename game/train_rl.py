"""
Trainer script placeholder inside game/ to avoid creating a new top-level scripts/ folder.
Run: python -m game.train_rl --output models/ppo_tie --timesteps 100000

Note: This is a lightweight helper. Install gym and stable-baselines3 to actually train.
"""
import argparse
import os

try:
    from game.train_simulator import HeadlessCombatEnv
except Exception as e:
    print('Failed to import training helpers:', e)
    raise

try:
    import gym
    from stable_baselines3 import PPO
except Exception:
    print('stable-baselines3 or gym not installed. Install with: pip install stable-baselines3[extra] gym')
    raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    p.add_argument('--timesteps', type=int, default=100000)
    args = p.parse_args()

    # TODO: Replace CartPole placeholder env with a wrapper around HeadlessCombatEnv
    env = gym.make('CartPole-v1')
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=args.timesteps)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    model.save(args.output)

if __name__ == '__main__':
    main()
