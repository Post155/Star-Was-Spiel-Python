"""
state_machine.py
Concrete State subclasses for EnemyShip and a small state-transition helper.
"""
from enum import Enum, auto
from typing import Optional
import math
import numpy as np


class AIState(Enum):
    PATROL = auto()
    SEARCH = auto()
    ATTACK = auto()
    EVADE = auto()
    RETREAT = auto()
    FLANK = auto()
    GUARD_LEADER = auto()


class State:
    def __init__(self, ai_controller):
        self.ai = ai_controller

    def enter(self, prev_state: Optional['State']):
        pass

    def exit(self):
        pass

    def update(self, dt: float):
        pass


class PatrolState(State):
    def enter(self, prev_state):
        self.waypoint = None

    def update(self, dt: float):
        world = self.ai_world()
        # simple orbit/patrol: pick a point near spawn or leader
        if self.waypoint is None:
            player = world.get('player')
            pos = np.array(self.ai.position)
            # choose waypoint offset
            self.waypoint = pos + np.array([100.0, 0.0])
        # use steering seek toward waypoint if steering component exists
        if getattr(self.ai, 'steering', None) is not None:
            ctx = {'target_pos': self.waypoint, 'neighbors': world.get('neighbors', []), 'obstacles': world.get('asteroids', [])}
            desired = self.ai.steering.compute(ctx)
            # store for visualization
            try:
                self.ai.last_desired_velocity = desired
            except Exception:
                pass
            from game.ai.controls_adapter import apply_steering_to_controls
            apply_steering_to_controls(self.ai, desired, dt)


class SearchState(State):
    def update(self, dt: float):
        # random exploration
        if getattr(self.ai, 'steering', None) is not None:
            import numpy as np
            rand_dir = np.array([np.random.uniform(-1,1), np.random.uniform(-1,1)])
            desired = rand_dir / (np.linalg.norm(rand_dir)+1e-9) * self.ai.stats.max_speed * 0.6
            from game.ai.controls_adapter import apply_steering_to_controls
            apply_steering_to_controls(self.ai, desired, dt)


class AttackState(State):
    def update(self, dt: float):
        world = self.ai_world()
        player = world.get('player')
        if player is None:
            return
        # pursuit + fire
        if getattr(self.ai, 'steering', None) is not None and world.get('player_agent') is not None:
            ctx = {'target_agent': world['player_agent'], 'neighbors': world.get('neighbors', []), 'obstacles': world.get('asteroids', [])}
            desired = self.ai.steering.compute(ctx)
            try:
                self.ai.last_desired_velocity = desired
            except Exception:
                pass
            from game.ai.controls_adapter import apply_steering_to_controls
            apply_steering_to_controls(self.ai, desired, dt)
        # let decision logic handle firing; state could set flags
        # simple transition: if low HP -> EVADE
        if self.ai.hp < self.ai.max_hp * 0.25:
            self.ai.state_machine.change_state(AIState.EVADE)


class EvadeState(State):
    def enter(self, prev_state):
        self.time = 0.0

    def update(self, dt: float):
        self.time += dt
        world = self.ai_world()
        threat = world.get('threat')
        if getattr(self.ai, 'steering', None) is not None and threat is not None:
            ctx = {'threat': threat, 'neighbors': world.get('neighbors', []), 'obstacles': world.get('asteroids', [])}
            desired = self.ai.steering.compute(ctx)
            try:
                self.ai.last_desired_velocity = desired
            except Exception:
                pass
            from game.ai.controls_adapter import apply_steering_to_controls
            apply_steering_to_controls(self.ai, desired, dt)
        if self.time > 2.0:
            self.ai.state_machine.change_state(AIState.ATTACK)


class RetreatState(State):
    def update(self, dt: float):
        # move away from player and find cover
        world = self.ai_world()
        player = world.get('player')
        if player is None:
            return
        dir_away = np.array(self.ai.position) - np.array(player['position'])
        if np.linalg.norm(dir_away) < 1e-6:
            dir_away = np.array([1.0, 0.0])
        desired = (dir_away / np.linalg.norm(dir_away)) * self.ai.stats.max_speed * 0.8
        from game.ai.controls_adapter import apply_steering_to_controls
        apply_steering_to_controls(self.ai, desired, dt)
        # if HP recovered or safe, go back to attack
        if self.ai.hp > self.ai.max_hp * 0.6:
            self.ai.state_machine.change_state(AIState.ATTACK)


class FlankState(State):
    def update(self, dt: float):
        # move to flank position computed by leader or utility
        world = self.ai_world()
        flank_point = self.ai.squad_context.get('flank_point') if hasattr(self.ai, 'squad_context') else None
        if flank_point is None and world.get('player') is not None:
            # compute flank from player
            ppos = np.array(world['player']['position'])
            offset = np.array([0.0, 150.0])
            flank_point = ppos + offset
        if getattr(self.ai, 'steering', None) is not None:
            ctx = {'target_pos': flank_point, 'neighbors': world.get('neighbors', []), 'obstacles': world.get('asteroids', [])}
            desired = self.ai.steering.compute(ctx)
            try:
                self.ai.last_desired_velocity = desired
            except Exception:
                pass
            from game.ai.controls_adapter import apply_steering_to_controls
            apply_steering_to_controls(self.ai, desired, dt)


class GuardLeaderState(State):
    def update(self, dt: float):
        # leaders hold position near a protected ship or waypoint
        target = self.ai.squad_context.get('guard_target')
        if target is None:
            return
        if getattr(self.ai, 'steering', None) is not None:
            ctx = {'target_pos': target.position if hasattr(target, 'position') else target, 'neighbors': [], 'obstacles': []}
            desired = self.ai.steering.compute(ctx)
            from game.ai.controls_adapter import apply_steering_to_controls
            apply_steering_to_controls(self.ai, desired, dt)


class StateMachine:
    def __init__(self, ai_controller):
        self.ai = ai_controller
        self.current_state = None
        self.current_enum = None
        # initialize neutral state
        self.change_state(AIState.PATROL)

    def change_state(self, new_state_enum: AIState):
        if self.current_state is not None:
            try:
                self.current_state.exit()
            except Exception:
                pass
        self.current_enum = new_state_enum
        mapping = {
            AIState.PATROL: PatrolState,
            AIState.SEARCH: SearchState,
            AIState.ATTACK: AttackState,
            AIState.EVADE: EvadeState,
            AIState.RETREAT: RetreatState,
            AIState.FLANK: FlankState,
            AIState.GUARD_LEADER: GuardLeaderState,
        }
        cls = mapping.get(new_state_enum, PatrolState)
        self.current_state = cls(self.ai)
        try:
            self.current_state.enter(None)
        except Exception:
            pass

    def update(self, dt: float):
        if self.current_state is not None:
            try:
                # expose a small world helper to the state via self.current_state.ai_world()
                def ai_world():
                    # minimal world info: player, player_agent, asteroids, neighbors
                    return {
                        'player': self.ai._last_world.get('player') if hasattr(self.ai, '_last_world') else None,
                        'player_agent': self.ai._last_world.get('player_agent') if hasattr(self.ai, '_last_world') else None,
                        'asteroids': self.ai._last_world.get('asteroids', []) if hasattr(self.ai, '_last_world') else [],
                        'neighbors': self.ai._last_world.get('neighbors', []) if hasattr(self.ai, '_last_world') else [],
                        'threat': self.ai._last_world.get('threat') if hasattr(self.ai, '_last_world') else None,
                    }
                # bind helper
                self.current_state.ai_world = ai_world
                self.current_state.update(dt)
            except Exception:
                pass