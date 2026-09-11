"""Enemy spawning, balancing, unlock progression, collisions and lifecycle."""
from __future__ import annotations

import random
from dataclasses import dataclass, replace

from game.constants import (
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
    ENEMY_UNLOCK_STANDARD_POINTS,
    ENEMY_UNLOCK_HEAVY_POINTS,
    ENEMY_UNLOCK_ELITE_POINTS,
    ENEMY_WARNING_DURATION_MS,
    SYSTEM_DIFFICULTY_BONUS,
    SYSTEM_PROGRESS_MAX_BONUS,
)

from game.entities.explosion import Explosion

from .base import EnemyBase
from .config import (
    ENEMY_ARCHETYPES,
    SHIP_NAME_BY_ASSET,
    SHIP_SCALE_BY_ASSET,
    opposing_ship_asset_key,
)


@dataclass
class EnemyUpdateResult:
    score_delta: int = 0
    player_dead: bool = False
    warning_text: str | None = None


class EnemyManager:
    """Central enemy controller.

    Difficulty is deliberately data-driven: change DIFFICULTY_SETTINGS and the
    unlock/system constants in game/constants.py to rebalance the game.
    """

    def __init__(self, width, height, assets, player, difficulty=DEFAULT_DIFFICULTY):
        self.width = width
        self.height = height
        self.assets = assets
        self.player = player
        self.difficulty = difficulty if difficulty in DIFFICULTY_SETTINGS else DEFAULT_DIFFICULTY
        self.enemies = []
        self.projectiles = []
        self.explosions = []
        self.spawn_timer = 1.0
        self._role_cursor = 0

        # Warnings are queued before the first enemy of a newly unlocked tier.
        self.warning_text = None
        self.warning_timer_ms = 0
        self.warning_pending_tier = None
        self.warned_tiers = set()

    def set_difficulty(self, difficulty):
        if difficulty in DIFFICULTY_SETTINGS:
            self.difficulty = difficulty

    def set_player(self, player, clear_existing=True):
        self.player = player
        if clear_existing:
            self.enemies.clear()
            self.projectiles.clear()
            self.spawn_timer = 1.0

    def resize(self, width, height):
        self.width = width
        self.height = height
        for enemy in self.enemies:
            enemy.resize(width, height)
        for explosion in self.explosions:
            explosion.resize(height)

    # ------------------------------------------------------------------
    # Difficulty calculation
    # ------------------------------------------------------------------
    def _profile(self):
        return DIFFICULTY_SETTINGS[self.difficulty]

    def _system_bonus(self, system_index):
        idx = max(0, int(system_index))
        if idx < len(SYSTEM_DIFFICULTY_BONUS):
            return SYSTEM_DIFFICULTY_BONUS[idx]
        return SYSTEM_DIFFICULTY_BONUS[-1]

    def _difficulty_scale(self, score, system_index):
        profile = self._profile()
        system_bonus = self._system_bonus(system_index)

        # Gentle score pressure after enemies are unlocked; it is capped.
        progress = 0.0
        if score > ENEMY_UNLOCK_STANDARD_POINTS:
            progress = min(
                SYSTEM_PROGRESS_MAX_BONUS,
                (score - ENEMY_UNLOCK_STANDARD_POINTS) / 5000.0
                * SYSTEM_PROGRESS_MAX_BONUS,
            )
        return max(0.75, 1.0 + system_bonus + progress)

    # ------------------------------------------------------------------
    # Enemy unlock progression
    # ------------------------------------------------------------------
    def _unlocked_tier(self, score):
        if score >= ENEMY_UNLOCK_ELITE_POINTS:
            return 3
        if score >= ENEMY_UNLOCK_HEAVY_POINTS:
            return 2
        if score >= ENEMY_UNLOCK_STANDARD_POINTS:
            return 1
        return 0

    def _tier_warning(self, tier):
        if tier == 1:
            return "Achtung! Feindliche Schiffe wurden entdeckt."
        if tier == 2:
            return "Warnung: Schwere Feinde im Anflug!"
        if tier == 3:
            return "WARNUNG: Elite-Einheit im Anflug!"
        return None

    def _check_unlock_warning(self, score):
        tier = self._unlocked_tier(score)

        if self.warning_pending_tier is not None:
            return

        for new_tier in (1, 2, 3):
            if tier >= new_tier and new_tier not in self.warned_tiers:
                self.warning_pending_tier = new_tier
                self.warning_text = self._tier_warning(new_tier)
                self.warning_timer_ms = ENEMY_WARNING_DURATION_MS
                return

    def _warning_active(self, dt):
        if self.warning_pending_tier is None:
            return False

        self.warning_timer_ms -= int(dt * 1000)
        if self.warning_timer_ms <= 0:
            self.warned_tiers.add(self.warning_pending_tier)
            self.warning_pending_tier = None
            self.warning_text = None
            return False
        return True

    # ------------------------------------------------------------------
    # Spawn balancing
    # ------------------------------------------------------------------
    def _max_enemies(self, score, system_index):
        profile = self._profile()
        scale = self._difficulty_scale(score, system_index)
        # Start at one enemy. Increase the cap gradually, not in sudden waves.
        base = 1 + min(5, int(max(0, score - 1000) // 1800))
        cap = int(round(base * profile["enemy_max"] * (1.0 + (scale - 1.0) * 0.45)))
        return max(1, min(8, cap))

    def _spawn_interval(self, score, system_index):
        profile = self._profile()
        scale = self._difficulty_scale(score, system_index)
        # The interval is intentionally conservative to avoid unfair waves.
        pressure = 1.0 + max(0.0, scale - 1.0) * 0.45
        interval = 2.60 * profile["enemy_spawn"] / pressure

        if score < ENEMY_UNLOCK_HEAVY_POINTS:
            interval += 0.55
        if score < ENEMY_UNLOCK_ELITE_POINTS:
            interval += 0.25
        return max(1.15, interval) * random.uniform(0.90, 1.12)

    def _choose_archetype(self, score, system_index):
        tier = self._unlocked_tier(score)
        scale = self._difficulty_scale(score, system_index)

        # Standard tier: standard + fast. Heavy appears only at 3000,
        # elite only at 6000.
        if tier <= 0:
            return None
        if tier == 1:
            return ENEMY_ARCHETYPES["fast"] if random.random() < 0.30 else ENEMY_ARCHETYPES["standard"]
        if tier == 2:
            roll = random.random()
            if roll < 0.14 + max(0, scale - 1.0) * 0.10:
                return ENEMY_ARCHETYPES["fast"]
            if roll < 0.36:
                return ENEMY_ARCHETYPES["heavy"]
            return ENEMY_ARCHETYPES["standard"]

        roll = random.random()
        if roll < 0.10 + max(0, scale - 1.0) * 0.08:
            return ENEMY_ARCHETYPES["elite"]
        if roll < 0.34:
            return ENEMY_ARCHETYPES["heavy"]
        if roll < 0.56:
            return ENEMY_ARCHETYPES["fast"]
        return ENEMY_ARCHETYPES["standard"]

    def _balanced_archetype(self, archetype, score, system_index):
        """Apply the selected difficulty and system progression to enemy stats."""
        p = self._profile()
        scale = self._difficulty_scale(score, system_index)
        system_factor = 1.0 + max(0.0, scale - 1.0)

        hp_factor = p["enemy_hp"] * (1.0 + (system_factor - 1.0) * 0.55)
        speed_factor = p["enemy_speed"] * (1.0 + (system_factor - 1.0) * 0.65)
        accuracy = min(0.96, archetype.accuracy * p["enemy_accuracy"] + max(0.0, scale - 1.0) * 0.025)

        aggression = p["enemy_aggression"] * (1.0 + (system_factor - 1.0) * 0.45)
        reaction_factor = max(0.72, min(1.20, 1.0 / aggression))

        r0, r1 = archetype.reaction_time
        reaction = (max(0.08, r0 * reaction_factor), max(0.12, r1 * reaction_factor))
        dodge = min(0.82, archetype.dodge_chance * (0.82 + 0.18 * aggression))
        torpedo_chance = min(0.65, archetype.torpedo_chance * (0.85 + 0.15 * aggression))

        return replace(
            archetype,
            max_hp=max(1, int(round(archetype.max_hp * hp_factor))),
            max_speed=archetype.max_speed * speed_factor,
            acceleration=archetype.acceleration * min(1.22, 0.90 + aggression * 0.10),
            accuracy=accuracy,
            reaction_time=reaction,
            dodge_chance=dodge,
            torpedo_chance=torpedo_chance,
        )

    def _choose_role(self):
        if not self.enemies:
            return "attacker"
        roles = ("attacker", "flanker_left", "flanker_right", "support")
        role = roles[self._role_cursor % len(roles)]
        self._role_cursor += 1
        return role

    def _spawn_position(self, sprite_width, sprite_height):
        margin = 12
        max_x = max(margin, self.width - sprite_width - margin)
        for _ in range(18):
            x = random.uniform(margin, max_x)
            y = random.uniform(-sprite_height * 0.10, max(18.0, self.height * 0.10))
            candidate_left = x - 24
            candidate_right = x + sprite_width + 24
            if not any(
                enemy.y <= self.height * 0.22
                and candidate_left < enemy.x + enemy.width + 24
                and candidate_right > enemy.x - 24
                for enemy in self.enemies
            ):
                return x, y

        slots = max(1, self.width // max(90, sprite_width + 35))
        slot = len(self.enemies) % slots
        x = min(max_x, margin + slot * ((self.width - margin * 2) / slots))
        return x, -sprite_height * 0.10

    def _spawn_enemy(self, score, system_index):
        asset_key = opposing_ship_asset_key(self.player)
        image = self.assets.get(asset_key)
        if image is None:
            return

        base_archetype = self._choose_archetype(score, system_index)
        if base_archetype is None:
            return
        archetype = self._balanced_archetype(base_archetype, score, system_index)

        ship_scale = SHIP_SCALE_BY_ASSET[asset_key]
        approx_width = max(24, image.get_width() * ship_scale * archetype.visual_scale_multiplier)
        approx_height = max(24, image.get_height() * ship_scale * archetype.visual_scale_multiplier)
        spawn_x, spawn_y = self._spawn_position(approx_width, approx_height)

        enemy = EnemyBase(
            image=image,
            ship_name=SHIP_NAME_BY_ASSET[asset_key],
            archetype=archetype,
            window_width=self.width,
            window_height=self.height,
            spawn_x=spawn_x,
            spawn_y=spawn_y,
            ship_scale=ship_scale,
            role=self._choose_role(),
            torpedo_image=self.assets.get("torpedo_img"),
            difficulty_scale=self._difficulty_scale(score, system_index),
        )
        self.enemies.append(enemy)

    @staticmethod
    def _player_projectile_damage(projectile):
        return 4 if "torpedo" in projectile.__class__.__name__.lower() else 1

    def _destroy_enemy(self, enemy, award_score=True):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        explosion_scale = max(0.55, min(1.20, enemy.visual_scale * 2.3))
        explosion_img = self.assets.get("explosion_img")
        if explosion_img is not None:
            self.explosions.append(
                Explosion(enemy.centerx, enemy.centery, explosion_scale, explosion_img, self.height)
            )
        return enemy.score_value() if award_score else 0

    def _handle_player_shots(self, player_lasers, player_torpedoes):
        score_delta = 0
        for projectile_list in (player_lasers, player_torpedoes):
            for projectile in projectile_list[:]:
                rect = getattr(projectile, "rect", None)
                if rect is None:
                    continue
                hit_enemy = next(
                    (enemy for enemy in self.enemies if enemy.alive and enemy.hitbox.colliderect(rect)),
                    None,
                )
                if hit_enemy is None:
                    continue

                if projectile in projectile_list:
                    projectile_list.remove(projectile)
                destroyed = hit_enemy.take_damage(self._player_projectile_damage(projectile))
                if destroyed:
                    score_delta += self._destroy_enemy(hit_enemy, award_score=True)
        return score_delta

    def _handle_enemy_projectiles(self):
        player_dead = False
        for projectile in self.projectiles[:]:
            if not projectile.alive:
                self.projectiles.remove(projectile)
                continue
            if projectile.rect.colliderect(self.player.hitbox):
                damage = max(1, int(getattr(projectile, "damage", 1)))
                player_dead = self.player.take_damage(damage) or player_dead
                projectile.alive = False
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
        return player_dead

    def _handle_ship_collisions(self):
        player_dead = False
        for enemy in self.enemies[:]:
            if enemy.alive and enemy.hitbox.colliderect(self.player.hitbox):
                player_dead = self.player.take_damage(1) or player_dead
                enemy.alive = False
                self._destroy_enemy(enemy, award_score=False)
        return player_dead

    def update(self, dt, score, system_difficulty=0, player_lasers=None, player_torpedoes=None):
        player_lasers = player_lasers if player_lasers is not None else []
        player_torpedoes = player_torpedoes if player_torpedoes is not None else []
        result = EnemyUpdateResult()

        self._check_unlock_warning(score)
        warning_was_active = self._warning_active(dt)

        # No enemies spawn while the warning is visible.
        if not warning_was_active:
            self.spawn_timer -= dt
            tier = self._unlocked_tier(score)
            if (
                tier > 0
                and self.warning_pending_tier is None
                and self.spawn_timer <= 0
                and len(self.enemies) < self._max_enemies(score, system_difficulty)
            ):
                self._spawn_enemy(score, system_difficulty)
                self.spawn_timer = self._spawn_interval(score, system_difficulty)

        difficulty_scale = self._difficulty_scale(score, system_difficulty)
        player_projectiles = list(player_lasers) + list(player_torpedoes)

        for enemy in self.enemies[:]:
            if enemy.alive:
                self.projectiles.extend(
                    enemy.update(
                        dt,
                        self.player,
                        player_projectiles,
                        self.enemies,
                        difficulty_scale=difficulty_scale,
                    )
                )

        for projectile in self.projectiles[:]:
            projectile.update(dt, self.width, self.height)
            if not projectile.alive and projectile in self.projectiles:
                self.projectiles.remove(projectile)

        result.score_delta += self._handle_player_shots(player_lasers, player_torpedoes)
        result.player_dead = self._handle_enemy_projectiles() or result.player_dead
        result.player_dead = self._handle_ship_collisions() or result.player_dead

        for explosion in self.explosions[:]:
            if explosion.update():
                self.explosions.remove(explosion)

        result.warning_text = self.warning_text
        return result

    def draw(self, screen, show_hitboxes=False):
        for enemy in self.enemies:
            enemy.draw(screen, show_hitbox=show_hitboxes)
        for projectile in self.projectiles:
            projectile.draw(screen)
        for explosion in self.explosions:
            explosion.draw(screen)
