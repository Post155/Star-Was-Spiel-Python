"""Steering / movement component for enemies."""
from __future__ import annotations

import math


class EnemyMovement:
    """Applies acceleration-limited steering for natural enemy motion."""

    def __init__(self, owner):
        self.owner = owner

    @staticmethod
    def _approach(current, target, max_delta):
        if current < target:
            return min(current + max_delta, target)
        return max(current - max_delta, target)

    def update(self, dt, target_x, target_y, dodge_velocity=0.0):
        enemy = self.owner
        dx = target_x - enemy.centerx
        dy = target_y - enemy.centery

        # Horizontal steering is the main combat axis. Dodge velocity is added
        # as a temporary impulse and then naturally decays via acceleration.
        desired_vx = max(-enemy.max_speed, min(enemy.max_speed, dx * 2.2)) + dodge_velocity
        desired_vx = max(-enemy.max_speed * 1.35, min(enemy.max_speed * 1.35, desired_vx))
        desired_vy = max(-enemy.max_speed * 0.55, min(enemy.max_speed * 0.55, dy * 1.4))

        max_change = enemy.acceleration * dt
        enemy.vx = self._approach(enemy.vx, desired_vx, max_change)
        enemy.vy = self._approach(enemy.vy, desired_vy, max_change * 0.72)

        # Clamp diagonal velocity so flanking cannot accidentally double speed.
        length = math.hypot(enemy.vx, enemy.vy)
        max_total = enemy.max_speed * 1.12
        if length > max_total:
            scale = max_total / length
            enemy.vx *= scale
            enemy.vy *= scale

        enemy.x += enemy.vx * dt
        enemy.y += enemy.vy * dt

        # Keep enemies in the combat area. They may touch the top edge but are
        # not allowed to leave sideways or dive onto the UI at the bottom.
        enemy.x = max(0.0, min(enemy.x, enemy.window_width - enemy.width))
        max_y = max(80.0, enemy.window_height * 0.58 - enemy.height)
        enemy.y = max(-enemy.height * 0.15, min(enemy.y, max_y))
        enemy.update_hitbox()
