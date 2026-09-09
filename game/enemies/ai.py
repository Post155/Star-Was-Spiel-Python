"""Decision-making component for AI enemies."""
from __future__ import annotations

import random


ROLE_OFFSETS = {
    "attacker": 0.0,
    "support": 0.18,
    "flanker_left": -0.26,
    "flanker_right": 0.26,
}

ROLE_Y = {
    "attacker": 0.34,
    "support": 0.18,
    "flanker_left": 0.27,
    "flanker_right": 0.27,
}


class EnemyBrain:
    """Low-cost tactical decision layer.

    Decisions happen on a reaction timer instead of every frame. This both
    avoids robotic perfection and keeps CPU usage predictable with many enemies.
    """

    def __init__(self, owner, role="attacker"):
        self.owner = owner
        self.role = role
        self.reaction_timer = random.uniform(*owner.archetype.reaction_time)
        self.target_x = owner.centerx
        self.target_y = max(owner.height, owner.window_height * ROLE_Y.get(role, 0.28))
        self.jitter = random.uniform(-55.0, 55.0)
        self.dodge_time = 0.0
        self.dodge_velocity = 0.0
        self.dodge_lockout = random.uniform(0.35, 0.8)
        self.strafe_sign = random.choice((-1, 1))

    def _projectile_threat(self, projectile):
        enemy = self.owner
        rect = getattr(projectile, "rect", None)
        if rect is None:
            return False

        # Player shots travel upward. Only consider shots below the enemy that
        # could enter its horizontal hitbox soon.
        vertical_distance = enemy.hitbox.bottom - rect.top
        if vertical_distance >= 0:
            return False

        speed_per_frame = float(getattr(projectile, "speed", 10.0))
        speed_per_second = max(60.0, speed_per_frame * 60.0)
        time_to_enemy = abs(vertical_distance) / speed_per_second
        if time_to_enemy > 0.72:
            return False

        margin = 22 + abs(enemy.vx) * min(0.20, time_to_enemy)
        return (enemy.hitbox.left - margin) <= rect.centerx <= (enemy.hitbox.right + margin)

    def _choose_dodge(self, player_projectiles, nearby_enemies):
        enemy = self.owner
        if self.dodge_lockout > 0:
            return
        if not any(self._projectile_threat(p) for p in player_projectiles):
            return
        if random.random() > enemy.archetype.dodge_chance:
            self.dodge_lockout = random.uniform(0.20, 0.55)
            return

        left_space = enemy.x
        right_space = enemy.window_width - (enemy.x + enemy.width)
        direction = -1 if left_space > right_space else 1

        # Avoid dodging into a nearby wingman when possible.
        for other in nearby_enemies:
            if other is enemy or not other.alive:
                continue
            if abs(other.centery - enemy.centery) < enemy.height * 1.5:
                if 0 < other.centerx - enemy.centerx < enemy.width * 2.0:
                    direction = -1
                elif 0 < enemy.centerx - other.centerx < enemy.width * 2.0:
                    direction = 1

        if random.random() < 0.25:
            direction *= -1

        self.dodge_velocity = direction * enemy.max_speed * random.uniform(1.05, 1.35)
        self.dodge_time = random.uniform(0.20, 0.46)
        self.dodge_lockout = random.uniform(0.65, 1.35)

    def update(self, dt, player, player_projectiles, nearby_enemies, difficulty_scale=1.0):
        enemy = self.owner
        self.reaction_timer -= dt
        self.dodge_lockout = max(0.0, self.dodge_lockout - dt)

        if self.dodge_time > 0:
            self.dodge_time -= dt
        else:
            self.dodge_velocity *= max(0.0, 1.0 - 7.0 * dt)

        if self.reaction_timer <= 0:
            player_center_x = player.hitbox.centerx
            role_offset = ROLE_OFFSETS.get(self.role, 0.0) * enemy.window_width

            # Slightly lead the player's recent movement. Elites lead more,
            # standard enemies retain visibly imperfect aim/tracking.
            lead = enemy.estimated_player_vx * (0.10 + enemy.archetype.accuracy * 0.18)
            self.jitter = random.uniform(-1.0, 1.0) * (80.0 * (1.0 - enemy.archetype.accuracy))
            self.target_x = player_center_x + role_offset + lead + self.jitter
            self.target_y = enemy.window_height * ROLE_Y.get(self.role, 0.28)

            # Attackers occasionally dive, supports intentionally keep distance.
            if self.role == "attacker" and random.random() < 0.17:
                self.target_y = enemy.window_height * random.uniform(0.38, 0.50)
            elif self.role == "support":
                self.target_y = enemy.window_height * random.uniform(0.13, 0.23)

            self._choose_dodge(player_projectiles, nearby_enemies)

            reaction_min, reaction_max = enemy.archetype.reaction_time
            reaction_factor = max(0.72, 1.0 / max(1.0, difficulty_scale * 0.08 + 1.0))
            self.reaction_timer = random.uniform(reaction_min, reaction_max) * reaction_factor

        return self.target_x, self.target_y, self.dodge_velocity
