"""Shared single-player simulation used by the PunkteKampf mode.

This module intentionally contains no PvP damage/collision rules. Each
PunkteKampf participant gets an independent copy of the normal single-player
world; multiplayer only exchanges lightweight score/position/system state.
"""
from __future__ import annotations

import pygame

from game.background import BackgroundManager
from game.constants import (
    ASTEROID_MIN_SPAWN_INTERVAL,
    ASTEROID_SPAWN_INTERVAL,
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
)
from game.enemies import EnemyManager
from game.entities.asteroid import Asteroid
from game.entities.explosion import Explosion
from game.entities.ships import BattleDroid, MillenniumFalcon, Tiefighter, XWing


class PointFightWorld:
    """One complete, normal single-player gameplay world."""

    def __init__(self, width, height, assets, ship_choice, difficulty=DEFAULT_DIFFICULTY):
        self.assets = assets
        self.ship_choice = ship_choice
        self.difficulty = difficulty if difficulty in DIFFICULTY_SETTINGS else DEFAULT_DIFFICULTY
        self.width = max(480, int(width))
        self.height = max(360, int(height))
        self.player = self._create_player()
        self.enemy_manager = EnemyManager(
            self.width, self.height, self.assets, self.player, difficulty=self.difficulty
        )
        self.background = BackgroundManager(self.width, self.height, self.assets)
        self.score = 0
        self.asteroid_spawn_timer = 0
        self.lasers = []
        self.torpedoes = []
        self.asteroids = []
        self.explosions = []
        self.dead = False
        self.warning_text = None
        self.warning_timer_ms = 0

    def _create_player(self):
        images = {
            "xwing": (XWing, "x_wing_img"),
            "milleniumfalcon": (MillenniumFalcon, "millennium_falcon_img"),
            "tiefighter": (Tiefighter, "tie_fighter_img"),
            "battledroid": (BattleDroid, "battle_droid_img"),
        }
        cls, asset_key = images.get(self.ship_choice, images["xwing"])
        return cls(
            self.width,
            self.height,
            self.assets[asset_key],
            self.assets.get("torpedo_img"),
        )

    @property
    def lives(self):
        return int(getattr(self.player, "lives", 0))

    @property
    def system_name(self):
        return self.background.get_current_system_name()

    @property
    def system_index(self):
        difficulty = self.background.get_current_difficulty()
        return int(difficulty.get("system_index", 0))

    def resize(self, width, height):
        self.width = max(480, int(width))
        self.height = max(360, int(height))
        self.player.resize(self.width, self.height)
        self.enemy_manager.resize(self.width, self.height)
        self.background.resize(self.width, self.height)
        for asteroid in self.asteroids:
            asteroid.resize(self.width, self.height)
        for explosion in self.explosions:
            explosion.resize(self.height)

    def set_ship(self, ship_choice):
        self.ship_choice = ship_choice
        self.player = self._create_player()
        self.enemy_manager.set_player(self.player, clear_existing=True)
        self.lasers.clear()
        self.torpedoes.clear()

    def shoot(self, weapon):
        if self.dead:
            return
        if weapon == "laser":
            shots = self.player.shoot()
            if shots:
                self.lasers.extend(shots)
        elif weapon == "torpedo":
            torpedo = self.player.torpedo()
            if torpedo:
                self.torpedoes.append(torpedo)

    def move(self, left, right):
        if self.dead:
            return
        if left and not right:
            self.player.move_left()
        elif right and not left:
            self.player.move_right(self.width)

    def _create_asteroid(self, speed_multiplier, size_multiplier):
        images = self.assets.get("asteroid_images", [])
        if not images:
            return None
        return Asteroid(
            self.width,
            self.height,
            images,
            size_multiplier=size_multiplier,
            speed_multiplier=speed_multiplier,
        )

    def update(self, dt):
        if self.dead:
            return

        for laser in self.lasers[:]:
            laser.update()
            if laser.rect.bottom < 0 and laser in self.lasers:
                self.lasers.remove(laser)

        for torpedo in self.torpedoes[:]:
            torpedo.update()
            if torpedo.rect.bottom < 0 and torpedo in self.torpedoes:
                self.torpedoes.remove(torpedo)

        difficulty = self.background.get_current_difficulty()
        system_index = int(difficulty.get("system_index", 0))
        system_bonus = float(difficulty.get("system_bonus", 0.0))
        profile = DIFFICULTY_SETTINGS[self.difficulty]

        asteroid_speed_multiplier = (
            float(difficulty.get("asteroid_speed_multiplier", 1.0))
            * profile["asteroid_speed"]
            * (1.0 + system_bonus * 0.70)
        )
        asteroid_density = profile["asteroid_density"] * (1.0 + system_bonus * 0.80)
        asteroid_interval = max(
            ASTEROID_MIN_SPAWN_INTERVAL,
            int(ASTEROID_SPAWN_INTERVAL / max(0.35, asteroid_density)),
        )

        self.asteroid_spawn_timer += 1
        if self.asteroid_spawn_timer >= asteroid_interval:
            asteroid = self._create_asteroid(
                asteroid_speed_multiplier,
                profile["asteroid_size"] * (1.0 + system_bonus * 0.18),
            )
            if asteroid is not None:
                self.asteroids.append(asteroid)
            self.asteroid_spawn_timer = 0

        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.y > self.height and asteroid in self.asteroids:
                self.asteroids.remove(asteroid)

        # Keep the exact single-player collision priority: projectile -> asteroid,
        # then asteroid -> player, then AI enemy simulation.
        for asteroid in self.asteroids[:]:
            asteroid_rect = asteroid.get_rect()
            hit_projectile = None
            for laser in self.lasers[:]:
                if asteroid_rect.colliderect(laser.rect):
                    hit_projectile = laser
                    break
            if hit_projectile is None:
                for torpedo in self.torpedoes[:]:
                    if asteroid_rect.colliderect(torpedo.rect):
                        hit_projectile = torpedo
                        break
            if hit_projectile is not None:
                self.score += asteroid.get_points()
                self._destroy_asteroid(asteroid)
                if asteroid in self.asteroids:
                    self.asteroids.remove(asteroid)
                if hit_projectile in self.lasers:
                    self.lasers.remove(hit_projectile)
                if hit_projectile in self.torpedoes:
                    self.torpedoes.remove(hit_projectile)

        for asteroid in self.asteroids[:]:
            if asteroid.get_rect().colliderect(self.player.hitbox):
                if self.player.is_invulnerable():
                    continue
                died = self.player.take_damage()
                self._destroy_asteroid(asteroid)
                if asteroid in self.asteroids:
                    self.asteroids.remove(asteroid)
                if died:
                    self.dead = True
                break

        enemy_result = self.enemy_manager.update(
            dt=dt,
            score=self.score,
            system_difficulty=system_index,
            player_lasers=self.lasers,
            player_torpedoes=self.torpedoes,
        )
        self.score += enemy_result.score_delta
        if enemy_result.player_dead or self.player.lives <= 0:
            self.dead = True
        self.warning_text = enemy_result.warning_text
        self.warning_timer_ms = self.enemy_manager.warning_timer_ms
        self.background.update(self.score)

        for explosion in self.explosions[:]:
            if explosion.update() and explosion in self.explosions:
                self.explosions.remove(explosion)

    def _destroy_asteroid(self, asteroid):
        image = self.assets.get("explosion_img")
        if image is not None:
            self.explosions.append(
                Explosion(
                    asteroid.x + asteroid.width // 2,
                    asteroid.y + asteroid.height // 2,
                    asteroid.scale,
                    image,
                    asteroid.window_height,
                )
            )

    def draw(self, screen, draw_hud=True, ghost_alpha=255):
        self.background.draw(screen)
        self.enemy_manager.draw(screen, show_hitboxes=self.player.show_hitbox)
        self.player.draw(screen)
        for laser in self.lasers:
            laser.draw(screen)
        for torpedo in self.torpedoes:
            torpedo.draw(screen)
        for asteroid in self.asteroids:
            asteroid.draw(screen)
        for explosion in self.explosions:
            explosion.draw(screen)
