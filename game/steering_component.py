"""
steering_component.py
Combines steering behaviors into a single steering output using configurable weights.
"""
import numpy as np
from typing import Dict, Any

from game import steering as steering_mod


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
        # target_agent, target_pos, neighbors, obstacles keys are expected in context
        if self.behavior_weights.get('pursuit', 0.0) > 0 and context.get('target_agent') is not None:
            total += steering_mod.pursuit(self.owner, context['target_agent'], self.max_speed) * self.behavior_weights['pursuit']
        if self.behavior_weights.get('evade', 0.0) > 0 and context.get('threat') is not None:
            total += steering_mod.evade(self.owner, context['threat'], self.max_speed) * self.behavior_weights['evade']
        if self.behavior_weights.get('separation', 0.0) > 0:
            total += steering_mod.separation(self.owner, context.get('neighbors', []), 30, self.max_force) * self.behavior_weights['separation']
        if self.behavior_weights.get('cohesion', 0.0) > 0:
            total += steering_mod.cohesion(self.owner, context.get('neighbors', []), self.max_speed) * self.behavior_weights['cohesion']
        if self.behavior_weights.get('obstacle_avoid', 0.0) > 0:
            total += steering_mod.obstacle_avoidance(self.owner, context.get('obstacles', []), 100, self.max_force) * self.behavior_weights['obstacle_avoid']

        # clamp
        norm = np.linalg.norm(total)
        if norm > self.max_force and norm > 1e-6:
            total = (total / norm) * self.max_force
        return total
