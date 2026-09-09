"""Enemy spawning, group tactics, collisions, scoring and lifecycle."""
from __future__ import annotations

import random
from dataclasses import dataclass

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


class EnemyManager:
    """High-level facade used by StarWarsGame.py.

    The main loop only needs update/draw/resize. Internally the manager keeps
    spawning, group roles, projectiles, explosions and difficulty scaling apart
    from the rest of the game, which makes wave/boss/co-op extensions easier.
    """

    def __init__(self, width, height, assets, player):
        self.width = width
        self.height = height
        self.assets = assets
        self.player = player
        self.enemies = []
        self.projectiles = []
        self.explosions = []
        self.spawn_timer = 0.55
        self.audio = EnemyAudio()
        self._role_cursor = 0

    def set_player(self, player, clear_existing=True):
        """Update player reference and guarantee the opposition rule."""
        self.player = player
        if clear_existing:
            self.enemies.clear()
            self.projectiles.clear()
            self.spawn_timer = 0.30

    def _difficulty_scale(self, score, system_difficulty):
        return max(1.0, float(system_difficulty) + min(8.0, score / 1400.0))

    def _max_enemies(self, score, system_difficulty):
        return min(12, 2 + int(system_difficulty) + int(score // 1300))

    def _spawn_interval(self, score, system_difficulty):
        pressure = 1.0 + system_difficulty * 0.16 + min(1.65, score / 5200.0)
        return max(0.46, 1.85 / pressure)

    def _choose_archetype(self, score, system_difficulty):
        difficulty_scale = self._difficulty_scale(score, system_difficulty)
        elite_weight = min(0.36, 0.015 + score / 18000.0 + system_difficulty * 0.018)
        heavy_weight = min(0.28, 0.10 + difficulty_scale * 0.012)
        fast_weight = min(0.32, 0.20 + difficulty_scale * 0.010)
        roll = random.random()
        if roll < elite_weight:
            return ENEMY_ARCHETYPES["elite"]
        if roll < elite_weight + heavy_weight:
            return ENEMY_ARCHETYPES["heavy"]
        if roll < elite_weight + heavy_weight + fast_weight:
            return ENEMY_ARCHETYPES["fast"]
        return ENEMY_ARCHETYPES["standard"]

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
            overlaps = False
            for enemy in self.enemies:
                if enemy.y > self.height * 0.22:
                    continue
                if candidate_left < enemy.x + enemy.width and candidate_right > enemy.x:
                    overlaps = True
                    break
            if not overlaps:
                return x, y
        # Deterministic fallback when the top lane is crowded.
        slots = max(1, self.width // max(90, sprite_width + 35))
        slot = len(self.enemies) % slots
        x = min(max_x, margin + slot * ((self.width - margin * 2) / slots))
        return x, -sprite_height * 0.10

    def _spawn_enemy(self, score, system_difficulty):
        asset_key = opposing_ship_asset_key(self.player)
        image = self.assets.get(asset_key)
        if image is None:
            return

        archetype = self._choose_archetype(score, system_difficulty)
        ship_scale = SHIP_SCALE_BY_ASSET[asset_key]
        approx_width = max(24, image.get_width() * ship_scale * archetype.visual_scale_multiplier)
        approx_height = max(24, image.get_height() * ship_scale * archetype.visual_scale_multiplier)
        spawn_x, spawn_y = self._spawn_position(approx_width, approx_height)
        difficulty_scale = self._difficulty_scale(score, system_difficulty)

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
            difficulty_scale=difficulty_scale,
        )
        self.enemies.append(enemy)

    @staticmethod
    def _player_projectile_damage(projectile):
        name = projectile.__class__.__name__.lower()
        return 4 if "torpedo" in name else 1

    def _destroy_enemy(self, enemy, award_score=True):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        explosion_scale = max(0.55, min(1.20, enemy.visual_scale * 2.3))
        explosion_img = self.assets.get("explosion_img")
        if explosion_img is not None:
            self.explosions.append(
                Explosion(enemy.centerx, enemy.centery, explosion_scale, explosion_img, self.height)
            )
        self.audio.play_explosion()
        return enemy.score_value() if award_score else 0

    def _handle_player_shots(self, player_lasers, player_torpedoes):
        score_delta = 0
        all_lists = (player_lasers, player_torpedoes)
        for projectile_list in all_lists:
            for projectile in projectile_list[:]:
                rect = getattr(projectile, "rect", None)
                if rect is None:
                    continue
                hit_enemy = None
                for enemy in self.enemies:
                    if enemy.alive and enemy.hitbox.colliderect(rect):
                        hit_enemy = enemy
                        break
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

    def update(self, dt, score, system_difficulty, player_lasers, player_torpedoes):
        result = EnemyUpdateResult()
        difficulty_scale = self._difficulty_scale(score, system_difficulty)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and len(self.enemies) < self._max_enemies(score, system_difficulty):
            # Higher difficulties can occasionally insert a second ship in the
            # same spawn cycle, subject to the global enemy cap.
            spawn_count = 1
            if system_difficulty >= 3 and random.random() < min(0.42, 0.08 * system_difficulty):
                spawn_count = 2
            for _ in range(spawn_count):
                if len(self.enemies) >= self._max_enemies(score, system_difficulty):
                    break
                self._spawn_enemy(score, system_difficulty)
            self.spawn_timer = self._spawn_interval(score, system_difficulty) * random.uniform(0.82, 1.18)

        player_projectiles = list(player_lasers) + list(player_torpedoes)
        for enemy in self.enemies[:]:
            if not enemy.alive:
                continue
            new_projectiles = enemy.update(
                dt,
                self.player,
                player_projectiles,
                self.enemies,
                difficulty_scale=difficulty_scale,
            )
            self.projectiles.extend(new_projectiles)

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

        return result

    def resize(self, width, height):
        self.width = width
        self.height = height
        for enemy in self.enemies:
            enemy.resize(width, height)
        for explosion in self.explosions:
            explosion.resize(height)

    def draw(self, screen, show_hitboxes=False):
        for enemy in self.enemies:
            enemy.draw(screen, show_hitbox=show_hitboxes)
        for projectile in self.projectiles:
            projectile.draw(screen)
        for explosion in self.explosions:
            explosion.draw(screen)
