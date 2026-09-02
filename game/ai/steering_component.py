"""
steering_component.py
Combines steering behaviors into a single steering output using configurable weights.
"""
import numpy as np
from typing import Dict, Any

from game.ai import steering as steering_mod


class SteeringComponent:
    def __init__(self, owner, max_speed: float, max_force: float):
        self.owner = owner
        self.max_speed = float(max_speed)
        self.max_force = float(max_force)
        # default weights
        self.behavior_weights: Dict[str, float] = {
            'seek': 0.0,
            'pursuit': 0.0,
            'evade': 0.0,
            'arrive': 0.0,
            'separation': 0.5,
            'cohesion': 0.0,
            'obstacle_avoid': 1.0,
        }

    def compute(self, context: Dict[str, Any]) -> np.ndarray:
        total = np.zeros(2, dtype=np.float64)
        # adapt radii based on ship speed / skill for more natural reactions
        separation_radius = max(30.0, self.owner.stats.max_speed * 0.08)
        avoid_distance = max(120.0, self.owner.stats.max_speed * 0.35)
        # allow owner override
        if hasattr(self.owner, 'sensing_radius') and self.owner.sensing_radius is not None:
            avoid_distance = max(avoid_distance, float(self.owner.sensing_radius))

        # target_agent, target_pos, neighbors, obstacles keys are expected in context
        if self.behavior_weights.get('pursuit', 0.0) > 0 and context.get('target_agent') is not None:
            total += steering_mod.pursuit(self.owner, context['target_agent'], self.max_speed) * self.behavior_weights['pursuit']
        if self.behavior_weights.get('evade', 0.0) > 0 and context.get('threat') is not None:
            total += steering_mod.evade(self.owner, context['threat'], self.max_speed) * self.behavior_weights['evade']
        if self.behavior_weights.get('separation', 0.0) > 0:
            total += steering_mod.separation(self.owner, context.get('neighbors', []), separation_radius, self.max_force) * self.behavior_weights['separation']
        if self.behavior_weights.get('cohesion', 0.0) > 0:
            total += steering_mod.cohesion(self.owner, context.get('neighbors', []), self.max_speed) * self.behavior_weights['cohesion']
        if self.behavior_weights.get('obstacle_avoid', 0.0) > 0:
            total += steering_mod.obstacle_avoidance(self.owner, context.get('obstacles', []), avoid_distance, self.max_force) * self.behavior_weights['obstacle_avoid']

        # clamp force
        norm = np.linalg.norm(total)
        if norm > self.max_force and norm > 1e-6:
            total = (total / norm) * self.max_force

        # convert force-like steering into a desired velocity vector to match controls_adapter expectations
        desired_velocity = np.array(self.owner.velocity, dtype=np.float64) + total
        vnorm = np.linalg.norm(desired_velocity)
        if vnorm > self.max_speed and vnorm > 1e-6:
            desired_velocity = (desired_velocity / vnorm) * self.max_speed
        return desired_velocity