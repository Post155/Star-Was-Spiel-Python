"""
game.enemy_ai

Hybrid AI scaffold for adaptive, RL-capable enemy pilots.
Place this file inside the game's package so it can be imported as game.enemy_ai.

Features:
- Ship types, stats and personalities
- Player profiling and persistent profile updates
- Observation and action spaces suitable for RL + utility evaluation
- Lightweight RLAgent wrapper for inference (Torch optional)
- UtilityEvaluator for high-frequency cheap decisions
- Simplified Behavior Tree primitives for mid-level tactics
- SquadController for cooperative behaviors
- EnemyShip class demonstrating direct integration (no separate API required)
- Performance tips and batched inference helper

This file is a scaffold: training should be done offline in a headless simulator
that uses the same observation/action interfaces provided here.
"""

from __future__ import annotations
import math
import random
import time
import json
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pygame
from game.constants import SHIP_SCALE_TIEFIGHTER, SHIP_SCALE_MILLENNIUM, SHIP_SCALE_XWING, SHIP_SCALE_BATTLEDROID

# Optional imports (only needed for Torch-based inference)
try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False

# Additional AI helper modules (lightweight, optional)
# These modules provide DecisionTick, StateMachine and aiming/steering helpers.
# If they are not present the code falls back to existing behavior.
from game.decision_tick import DecisionTick
from game.state_machine import StateMachine, AIState
from game.aim_utils import leading_position, compute_shot_direction
from game.steering_component import SteeringComponent


class ShipType(Enum):
    TIE_FIGHTER = "TIE_Fighter"
    TIE_INTERCEPTOR = "TIE_Interceptor"
    TIE_BOMBER = "TIE_Bomber"
    TIE_DEFENDER = "TIE_Defender"
    ELITE_BOSS = "Elite_Boss"


@dataclass
class ShipStats:
    max_speed: float
    turn_rate: float
    aggressiveness: float  # 0..1
    accuracy: float  # 0..1
    hp: float
    special_cooldown: float = 0.0


DEFAULT_STATS: Dict[ShipType, ShipStats] = {
    ShipType.TIE_FIGHTER: ShipStats(300.0, 200.0, 0.6, 0.6, 50.0),
    ShipType.TIE_INTERCEPTOR: ShipStats(380.0, 300.0, 0.8, 0.7, 40.0),
    ShipType.TIE_BOMBER: ShipStats(200.0, 80.0, 0.4, 0.5, 120.0),
    ShipType.TIE_DEFENDER: ShipStats(320.0, 220.0, 0.7, 0.75, 80.0),
    ShipType.ELITE_BOSS: ShipStats(250.0, 150.0, 0.9, 0.85, 500.0),
}


@dataclass
class Personality:
    name: str
    aggression_bias: float
    caution_bias: float
    maneuver_skill: float
    accuracy_bonus: float
    risk_tolerance: float

    @staticmethod
    def random_variant(role: Optional[str] = None) -> 'Personality':
        base = role or "pilot"
        if base == "aggressive":
            return Personality(
                name="Aggressive",
                aggression_bias=0.4,
                caution_bias=-0.2,
                maneuver_skill=random.uniform(0.4, 0.8),
                accuracy_bonus=random.uniform(0.0, 0.15),
                risk_tolerance=random.uniform(0.7, 1.0),
            )
        if base == "cautious":
            return Personality(
                name="Cautious",
                aggression_bias=-0.3,
                caution_bias=0.5,
                maneuver_skill=random.uniform(0.3, 0.6),
                accuracy_bonus=random.uniform(-0.05, 0.05),
                risk_tolerance=random.uniform(0.0, 0.4),
            )
        return Personality(
            name=f"Pilot-{random.randint(1000,9999)}",
            aggression_bias=random.uniform(-0.2, 0.3),
            caution_bias=random.uniform(-0.2, 0.3),
            maneuver_skill=random.random(),
            accuracy_bonus=random.uniform(-0.05, 0.2),
            risk_tolerance=random.random(),
        )


@dataclass
class PlayerProfile:
    player_id: str
    hit_rate: float = 0.0
    preferred_direction: float = 0.0
    favorite_weapon: Optional[str] = None
    avg_combat_distance: float = 0.0
    dodge_pattern: Dict[str, float] = field(default_factory=dict)
    favorite_targets: Dict[str, float] = field(default_factory=dict)
    encounter_count: int = 0

    def update_from_combat(self, data: Dict[str, Any]):
        alpha = 0.1
        self.encounter_count += 1
        if data.get('shots', 0) > 0:
            hr = data.get('hits', 0) / max(1, data.get('shots', 1))
            self.hit_rate = (1 - alpha) * self.hit_rate + alpha * hr
        if 'direction' in data:
            self.preferred_direction = (1 - alpha) * self.preferred_direction + alpha * data['direction']
        if 'distance' in data:
            self.avg_combat_distance = (1 - alpha) * self.avg_combat_distance + alpha * data['distance']
        if 'weapon' in data:
            self.favorite_weapon = data['weapon']
        for k, v in data.get('dodges', {}).items():
            self.dodge_pattern[k] = self.dodge_pattern.get(k, 0.0) * (1 - alpha) + v * alpha
        for k, v in data.get('targets', {}).items():
            self.favorite_targets[k] = self.favorite_targets.get(k, 0.0) * (1 - alpha) + v * alpha

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(s: str) -> 'PlayerProfile':
        d = json.loads(s)
        return PlayerProfile(**d)


@dataclass
class Observation:
    health_norm: float
    rel_vel: Tuple[float, float]
    rel_pos: Tuple[float, float]
    enemy_heading: float
    distance: float
    nearest_ally_dist: float
    nearest_asteroid_dist: float
    ammo_level: float
    cooldown_ready: float
    player_profile_vector: Optional[np.ndarray] = None

    def to_vector(self) -> np.ndarray:
        parts = [self.health_norm, self.rel_vel[0], self.rel_vel[1], self.rel_pos[0], self.rel_pos[1],
                 self.enemy_heading, self.distance, self.nearest_ally_dist, self.nearest_asteroid_dist,
                 self.ammo_level, self.cooldown_ready]
        if self.player_profile_vector is not None:
            parts.extend(list(self.player_profile_vector.flatten()))
        return np.array(parts, dtype=np.float32)


class Action(Enum):
    THRUST = auto()
    BRAKE = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    FIRE_PRIMARY = auto()
    FIRE_SECONDARY = auto()
    SPECIAL = auto()
    EVADE = auto()
    NONE = auto()


class RLAgent:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.device = 'cpu'
        if TORCH_AVAILABLE:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def load(self, model_path: Optional[str] = None):
        model_path = model_path or self.model_path
        if model_path is None:
            return
        self.model_path = model_path
        if TORCH_AVAILABLE and model_path.endswith('.pt'):
            try:
                self.model = torch.jit.load(model_path, map_location=self.device)
            except Exception:
                self.model = torch.load(model_path, map_location=self.device)
        else:
            self.model = None

    def infer(self, obs_vector: np.ndarray) -> Action:
        if self.model is None:
            return self.heuristic_policy(obs_vector)
        if TORCH_AVAILABLE and isinstance(self.model, torch.ScriptModule):
            with torch.no_grad():
                t = torch.from_numpy(obs_vector).float().to(self.device)
                logits = self.model(t.unsqueeze(0))
                action_idx = int(torch.argmax(logits).cpu().numpy())
                return list(Action)[action_idx]
        return self.heuristic_policy(obs_vector)

    @staticmethod
    def heuristic_policy(obs_vector: np.ndarray) -> Action:
        dist = float(obs_vector[6]) if obs_vector.shape[0] > 6 else 1000.0
        if dist < 100.0:
            return Action.FIRE_PRIMARY
        if dist < 300.0:
            return Action.THRUST
        return Action.NONE

    def save(self, path: str):
        if TORCH_AVAILABLE and hasattr(self.model, 'save'):
            self.model.save(path)


class UtilityEvaluator:
    def __init__(self, personality: Personality, stats: ShipStats):
        self.personality = personality
        self.stats = stats

    def score_action(self, obs: Observation, action: Action) -> float:
        score = 0.0
        if action == Action.FIRE_PRIMARY:
            score += 10.0 * (self.stats.accuracy + self.personality.accuracy_bonus)
            score += max(0.0, (1.0 - obs.health_norm) * 5.0)
            score += max(0.0, (1.0 - obs.distance / 1000.0) * 8.0)
            score *= (1.0 + self.personality.aggression_bias)
        if action == Action.EVADE:
            score += (1.0 - obs.health_norm) * 12.0
            score += max(0.0, (1.0 - obs.nearest_asteroid_dist / 500.0) * 6.0)
            score *= (1.0 + self.personality.caution_bias)
        if action == Action.THRUST:
            score += (0.5 + self.personality.maneuver_skill) * 3.0
            score += (1.0 - obs.distance / 1000.0) * 1.0
        if action == Action.SPECIAL:
            score += random.random() * 2.0
            if obs.cooldown_ready > 0.9:
                score += 5.0
        return score

    def choose(self, obs: Observation, candidate_actions: List[Action]) -> Action:
        best = Action.NONE
        best_score = -1e9
        for a in candidate_actions:
            s = self.score_action(obs, a)
            if s > best_score:
                best_score = s
                best = a
        return best


class BTNodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


class BTNode:
    def tick(self, context: Dict[str, Any]) -> BTNodeStatus:
        raise NotImplementedError()


class Sequence(BTNode):
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, context: Dict[str, Any]) -> BTNodeStatus:
        for c in self.children:
            s = c.tick(context)
            if s != BTNodeStatus.SUCCESS:
                return s
        return BTNodeStatus.SUCCESS


class Selector(BTNode):
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, context: Dict[str, Any]) -> BTNodeStatus:
        for c in self.children:
            s = c.tick(context)
            if s == BTNodeStatus.SUCCESS:
                return BTNodeStatus.SUCCESS
            if s == BTNodeStatus.RUNNING:
                return BTNodeStatus.RUNNING
        return BTNodeStatus.FAILURE


class Condition(BTNode):
    def __init__(self, func):
        self.func = func

    def tick(self, context: Dict[str, Any]) -> BTNodeStatus:
        return BTNodeStatus.SUCCESS if self.func(context) else BTNodeStatus.FAILURE


class ActionNode(BTNode):
    def __init__(self, func):
        self.func = func

    def tick(self, context: Dict[str, Any]) -> BTNodeStatus:
        try:
            res = self.func(context)
            if res:
                return BTNodeStatus.SUCCESS
            return BTNodeStatus.FAILURE
        except Exception:
            return BTNodeStatus.FAILURE


@dataclass
class SquadRoleAssignment:
    leader_id: Optional[int] = None
    flankers: List[int] = field(default_factory=list)
    supporters: List[int] = field(default_factory=list)


class SquadController:
    def __init__(self, squad_id: int, members: List['EnemyShip']):
        self.squad_id = squad_id
        self.members = members
        self.assignment = SquadRoleAssignment()

    def update(self):
        best_score = -1e9
        leader = None
        for m in self.members:
            s = m.personality.maneuver_skill * (m.hp / m.max_hp) * (1 + m.stats.aggressiveness)
            if s > best_score:
                best_score = s
                leader = m
        if leader:
            self.assignment.leader_id = leader.instance_id
        for m in self.members:
            m.squad_context = {'leader_id': self.assignment.leader_id}


class EnemyShip:
    _instance_counter = 0

    def __init__(self, ship_type: ShipType, position: Tuple[float, float], heading: float,
                 personality: Optional[Personality] = None, stats: Optional[ShipStats] = None,
                 rl_model_path: Optional[str] = None):
        EnemyShip._instance_counter += 1
        self.instance_id = EnemyShip._instance_counter
        self.ship_type = ship_type
        self.stats = stats or DEFAULT_STATS[ship_type]
        self.personality = personality or Personality.random_variant()
        self.position = np.array(position, dtype=np.float32)
        self.heading = heading
        self.velocity = np.array([0.0, 0.0], dtype=np.float32)
        self.hp = self.stats.hp
        self.max_hp = self.stats.hp
        self.cooldowns: Dict[str, float] = {}
        self.squad_context: Dict[str, Any] = {}

        self.utility = UtilityEvaluator(self.personality, self.stats)
        self.bt_root: Optional[BTNode] = None
        self.rl_agent = RLAgent(rl_model_path)
        if rl_model_path:
            self.rl_agent.load(rl_model_path)

        self.mode = 'hybrid'
        self.combat_history: List[Dict[str, Any]] = []
        # buffer for projectiles created during this update, consumed by EnemyManager
        self.pending_projectiles: List[Dict[str, Any]] = []

        # Decision tick throttles heavy decisions (utility, RL inference, squad updates)
        # Default ~10 Hz - adjustable per-enemy later
        try:
            self.decision_tick = DecisionTick(frequency_hz=10)
        except Exception:
            # fallback: simple object with should_run always True
            class _AlwaysTick:
                def should_run(self, frame_index):
                    return True
            self.decision_tick = _AlwaysTick()
        self._frame_index = 0
        self._last_action = Action.NONE

        # lightweight state machine - states implemented in game.state_machine (optional)
        try:
            self.state_machine = StateMachine(self)
        except Exception:
            self.state_machine = None

        # steering component (optional). Use lazy import so missing module doesn't break runtime.
        try:
            self.steering = SteeringComponent(owner=self, max_speed=self.stats.max_speed, max_force=self.stats.max_speed * 0.5)
        except Exception:
            self.steering = None

    def update(self, dt: float, world_state: Dict[str, Any]):
        # frame accounting for DecisionTick
        self._frame_index += 1

        # update state machine lightweightly if available
        if getattr(self, 'state_machine', None) is not None:
            try:
                self.state_machine.update(dt)
            except Exception:
                pass

        # cheap observation every frame
        obs = self._observe(world_state)

        # default to repeating last action when not re-evaluating
        action = self._last_action

        # run heavy decision logic only when DecisionTick allows
        try:
            should_run = self.decision_tick.should_run(self._frame_index)
        except Exception:
            should_run = True

        if should_run:
            if self.mode == 'utility':
                action = self._decide_utility(obs)
            elif self.mode == 'rl':
                action = self._decide_rl(obs)
            else:
                candidates = [Action.THRUST, Action.TURN_LEFT, Action.TURN_RIGHT, Action.FIRE_PRIMARY, Action.EVADE, Action.SPECIAL]
                u_choice = self.utility.choose(obs, candidates)
                if self.rl_agent.model is not None:
                    vec = obs.to_vector()
                    rl_choice = self.rl_agent.infer(vec)
                    if rl_choice in (Action.EVADE, Action.FIRE_PRIMARY, Action.SPECIAL):
                        action = rl_choice
                    else:
                        action = u_choice
                else:
                    action = u_choice
            self._last_action = action

        # execute the chosen or repeated action; pass world_state for predictive decisions (e.g. aiming)
        self._execute_action(action, dt, world_state)
        self._record_telemetry(action, obs, world_state)

    def _observe(self, world_state: Dict[str, Any]) -> Observation:
        player = world_state.get('player')
        nearest_ally = world_state.get('nearest_ally_distance', 10000.0)
        nearest_asteroid = world_state.get('nearest_asteroid_distance', 10000.0)

        rel_pos = player['position'] - self.position
        dist = float(np.linalg.norm(rel_pos))
        rel_vel = player['velocity'] - self.velocity

        health_norm = max(0.0, min(1.0, self.hp / self.max_hp))

        player_profile_vec = None
        pprofile: Optional[PlayerProfile] = world_state.get('player_profile')
        if pprofile is not None:
            player_profile_vec = np.array([
                pprofile.hit_rate,
                pprofile.avg_combat_distance / 1000.0,
                pprofile.encounter_count / max(1, pprofile.encounter_count + 1),
            ], dtype=np.float32)

        return Observation(
            health_norm=health_norm,
            rel_vel=(float(rel_vel[0]), float(rel_vel[1])),
            rel_pos=(float(rel_pos[0]), float(rel_pos[1])),
            enemy_heading=player.get('heading', 0.0),
            distance=dist,
            nearest_ally_dist=nearest_ally,
            nearest_asteroid_dist=nearest_asteroid,
            ammo_level=world_state.get('ammo_frac', 1.0),
            cooldown_ready=1.0 if self.cooldowns.get('special', 0.0) <= 0 else 0.0,
            player_profile_vector=player_profile_vec,
        )

    def _decide_utility(self, obs: Observation) -> Action:
        candidates = [Action.THRUST, Action.TURN_LEFT, Action.TURN_RIGHT, Action.FIRE_PRIMARY, Action.EVADE, Action.SPECIAL]
        return self.utility.choose(obs, candidates)

    def _decide_rl(self, obs: Observation) -> Action:
        v = obs.to_vector()
        return self.rl_agent.infer(v)

    def _execute_action(self, action: Action, dt: float, world_state: Optional[Dict[str, Any]] = None):
        if action == Action.THRUST:
            rad = math.radians(self.heading)
            accel = np.array([math.cos(rad), math.sin(rad)]) * self.stats.max_speed * 0.5
            self.velocity += accel * dt
        elif action == Action.BRAKE:
            self.velocity *= 0.9
        elif action == Action.TURN_LEFT:
            self.heading -= self.stats.turn_rate * dt
        elif action == Action.TURN_RIGHT:
            self.heading += self.stats.turn_rate * dt
        elif action == Action.FIRE_PRIMARY:
            # pass world_state for predictive aiming if available
            try:
                self._fire_primary(world_state)
            except TypeError:
                # fallback to legacy signature
                self._fire_primary()
        elif action == Action.SPECIAL:
            self._use_special()
        elif action == Action.EVADE:
            perp = np.array([-self.velocity[1], self.velocity[0]])
            if np.linalg.norm(perp) < 1e-3:
                perp = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
            perp = perp / (np.linalg.norm(perp) + 1e-6)
            self.velocity += perp * self.stats.max_speed * 0.6
        # simple physics integration
        self.position += self.velocity * dt

    def _fire_primary(self, world_state: Optional[Dict[str, Any]] = None):
        # Predictive aiming: if world_state contains player pos/vel and a projectile speed is known,
        # compute a leading aim point. Fall back to legacy straight shots when data missing.
        acc = max(0.0, min(1.0, self.stats.accuracy + self.personality.accuracy_bonus))
        rad = math.radians(self.heading)
        spawn_x = float(self.position[0] + math.cos(rad) * 10.0)
        spawn_y = float(self.position[1] + math.sin(rad) * 10.0)

        # default projectile speed (game units per tick) - keep same as legacy for consistency
        projectile_speed = 8.0

        aim_vx = math.cos(rad) * projectile_speed
        aim_vy = math.sin(rad) * projectile_speed

        if world_state is not None and world_state.get('player') is not None:
            try:
                player = world_state['player']
                # player position and velocity may be numpy arrays
                ppos = np.array(player.get('position'), dtype=np.float32)
                pvel = np.array(player.get('velocity'), dtype=np.float32)
                shooter_pos = np.array(self.position, dtype=np.float32)
                lead_point = leading_position(shooter_pos, ppos, pvel, projectile_speed)
                aim_dir = lead_point - shooter_pos
                if np.linalg.norm(aim_dir) > 1e-6:
                    aim_dir = aim_dir / (np.linalg.norm(aim_dir) + 1e-9)
                    aim_vx = float(aim_dir[0] * projectile_speed)
                    aim_vy = float(aim_dir[1] * projectile_speed)
            except Exception:
                # fallback to simple heading-based velocity
                pass

        # add some spread based on (1-acc)
        spread = (1.0 - acc) * 0.5
        aim_vx += random.uniform(-spread, spread)
        aim_vy += random.uniform(-spread, spread)

        proj = {
            'type': 'laser',
            'pos': (spawn_x, spawn_y),
            'vel': (aim_vx, aim_vy),
            'damage': 10,
            'source_id': self.instance_id,
        }
        self.pending_projectiles.append(proj)

    def get_rect(self) -> 'pygame.Rect':
        # approximate hitbox based on ship type and known sprite scales
        if self.ship_type == ShipType.TIE_FIGHTER:
            scale = SHIP_SCALE_TIEFIGHTER
        elif self.ship_type == ShipType.TIE_INTERCEPTOR:
            scale = SHIP_SCALE_TIEFIGHTER
        elif self.ship_type == ShipType.TIE_BOMBER:
            scale = SHIP_SCALE_TIEFIGHTER
        elif self.ship_type == ShipType.TIE_DEFENDER:
            scale = SHIP_SCALE_TIEFIGHTER
        elif self.ship_type == ShipType.ELITE_BOSS:
            scale = SHIP_SCALE_MILLENNIUM
        else:
            scale = 0.3
        w = int(80 * scale)
        h = int(80 * scale)
        rect = pygame.Rect(int(self.position[0] - w/2), int(self.position[1] - h/2), w, h)
        return rect

    def _use_special(self):
        if self.cooldowns.get('special', 0.0) <= 0.0:
            self.cooldowns['special'] = self.stats.special_cooldown or 5.0
            pass

    def _record_telemetry(self, action: Action, obs: Observation, world_state: Dict[str, Any]):
        self.combat_history.append({
            't': time.time(),
            'action': action.name,
            'obs': obs.to_vector().tolist(),
            'hp': self.hp,
            'pos': self.position.tolist(),
        })

    def finalize_encounter(self, player_profile: Optional[PlayerProfile] = None) -> Dict[str, Any]:
        summary = {
            'id': self.instance_id,
            'ship_type': self.ship_type.value,
            'personality': asdict(self.personality),
            'combat_history_len': len(self.combat_history),
            'survived': self.hp > 0,
            'telemetry': self.combat_history[-100:],
        }
        if player_profile is not None:
            p_data = {'hits': 0, 'shots': 0, 'direction': 0.0, 'distance': 0.0, 'dodges': {}, 'targets': {}}
            player_profile.update_from_combat(p_data)
        return summary


def batched_inference(rl_agent: RLAgent, obs_vectors: List[np.ndarray]) -> List[Action]:
    if rl_agent.model is None or not TORCH_AVAILABLE:
        return [rl_agent.heuristic_policy(v) for v in obs_vectors]
    with torch.no_grad():
        t = torch.from_numpy(np.stack(obs_vectors)).float().to(rl_agent.device)
        logits = rl_agent.model(t)
        idxs = torch.argmax(logits, dim=1).cpu().numpy().tolist()
        return [list(Action)[i] for i in idxs]


# Example debug run
if __name__ == "__main__":
    player = {'position': np.array([0.0, 0.0], dtype=np.float32), 'velocity': np.array([0.0, 0.0]), 'heading': 0.0}
    world_state = {'player': player, 'nearest_ally_distance': 900.0, 'nearest_asteroid_distance': 300.0, 'ammo_frac': 1.0}

    enemies = [EnemyShip(ShipType.TIE_FIGHTER, position=(random.uniform(-1000, 1000), random.uniform(-1000, 1000)), heading=random.uniform(0, 360)) for _ in range(6)]
    squad = SquadController(1, enemies)

    elite = EnemyShip(ShipType.ELITE_BOSS, position=(500, 0), heading=180, personality=Personality.random_variant('aggressive'))
    elite.mode = 'rl'

    print("Simulation step test...")
    dt = 1.0 / 60.0
    for frame in range(120):
        squad.update()
        world_state['player']['position'] = np.array([math.sin(frame * 0.1) * 200.0, 0.0])
        for e in enemies:
            e.update(dt, world_state)
        elite.update(dt, world_state)

    print("Done test run. Example enemy positions:")
    for e in enemies[:3]:
        print(e.instance_id, e.position.tolist(), e.hp)

# End of file
