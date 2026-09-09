"""Enemy weapon component: bursts, aimed lasers and tactical torpedoes."""
from __future__ import annotations

import random

from .projectiles import EnemyLaser, EnemyTorpedo


class EnemyWeaponSystem:
    def __init__(self, owner, torpedo_image=None):
        self.owner = owner
        self.torpedo_image = torpedo_image
        self.laser_timer = random.uniform(0.35, 1.2)
        self.torpedo_timer = random.uniform(*owner.archetype.torpedo_cooldown)
        self.burst_remaining = 0
        self.burst_timer = 0.0

    def _aim_point(self, player, difficulty_scale):
        enemy = self.owner
        distance_y = max(1.0, player.hitbox.centery - enemy.hitbox.centery)
        flight_time = min(0.75, distance_y / 470.0)

        # Accuracy improves with score/system difficulty, but is capped so the
        # player always has a fair chance to dodge.
        accuracy = min(0.97, enemy.archetype.accuracy + 0.015 * difficulty_scale)
        prediction = enemy.estimated_player_vx * flight_time * accuracy
        spread = (1.0 - accuracy) * 160.0
        target_x = player.hitbox.centerx + prediction + random.uniform(-spread, spread)
        target_y = player.hitbox.centery + random.uniform(-10.0, 18.0)
        return target_x, target_y

    def _fire_laser(self, player, difficulty_scale):
        target_x, target_y = self._aim_point(player, difficulty_scale)
        muzzle_x = self.owner.hitbox.centerx + random.choice((-1, 1)) * self.owner.width * 0.12
        muzzle_y = self.owner.hitbox.bottom - 4
        return EnemyLaser(
            muzzle_x,
            muzzle_y,
            target_x,
            target_y,
            damage=self.owner.archetype.laser_damage,
            speed=470.0 + min(90.0, difficulty_scale * 8.0),
        )

    def _can_use_torpedo(self, player):
        enemy = self.owner
        if player.hitbox.centery <= enemy.hitbox.centery:
            return False
        horizontal_error = abs(player.hitbox.centerx - enemy.hitbox.centerx)
        alignment_limit = max(55.0, enemy.width * 0.72)
        return horizontal_error <= alignment_limit

    def update(self, dt, player, difficulty_scale=1.0):
        spawned = []
        enemy = self.owner
        self.laser_timer -= dt
        self.torpedo_timer -= dt
        self.burst_timer -= dt

        if player.hitbox.centery <= enemy.hitbox.centery:
            return spawned

        if self.burst_remaining > 0 and self.burst_timer <= 0:
            spawned.append(self._fire_laser(player, difficulty_scale))
            self.burst_remaining -= 1
            self.burst_timer = random.uniform(0.08, 0.16)

        if self.burst_remaining <= 0 and self.laser_timer <= 0:
            low, high = enemy.archetype.burst_range
            self.burst_remaining = random.randint(low, high)
            self.burst_timer = 0.0
            cooldown_low, cooldown_high = enemy.archetype.laser_cooldown
            fire_rate_factor = max(0.58, 1.0 - difficulty_scale * 0.035)
            self.laser_timer = random.uniform(cooldown_low, cooldown_high) * fire_rate_factor

        if self.torpedo_timer <= 0 and self._can_use_torpedo(player):
            tactical_chance = min(0.92, enemy.archetype.torpedo_chance + difficulty_scale * 0.018)
            if random.random() < tactical_chance:
                target_x, target_y = self._aim_point(player, difficulty_scale)
                spawned.append(
                    EnemyTorpedo(
                        enemy.hitbox.centerx,
                        enemy.hitbox.bottom,
                        target_x,
                        target_y,
                        image=self.torpedo_image,
                        damage=enemy.archetype.torpedo_damage,
                        speed=285.0 + min(55.0, difficulty_scale * 5.0),
                    )
                )
            low, high = enemy.archetype.torpedo_cooldown
            self.torpedo_timer = random.uniform(low, high) / max(1.0, 1.0 + difficulty_scale * 0.03)

        return spawned
