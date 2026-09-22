"""Independent local Points Fight implementation.

Points Fight is deliberately NOT built on PvPDuelSession.  Every local player
owns a complete single-player simulation (asteroids, AI, projectiles, score and
star-system progression).  The two simulations only share the display and the
scoreboard; they never share gameplay objects or collision logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pygame

from game.background import BackgroundManager
from game.constants import (
    ASTEROID_MIN_SPAWN_INTERVAL,
    ASTEROID_SPAWN_INTERVAL,
    BLACK,
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
)
from game.enemies import EnemyManager
from game.entities.asteroid import Asteroid
from game.entities.explosion import Explosion
from game.entities.ships import BattleDroid, MillenniumFalcon, Tiefighter, XWing


@dataclass
class PointsPlayerConfig:
    name: str
    ship: str
    faction: str
    difficulty: str


class PointsFightWorld:
    """One complete, isolated single-player world for Points Fight."""

    def __init__(self, config: PointsPlayerConfig, assets: dict, width: int, height: int):
        self.config = config
        self.assets = assets
        self.width = max(320, int(width))
        self.height = max(360, int(height))
        self.player = self._create_player(config.ship)
        self.enemy_manager = EnemyManager(
            self.width,
            self.height,
            assets,
            self.player,
            difficulty=config.difficulty,
        )
        self.background = BackgroundManager(self.width, self.height, assets)
        self.asteroids: list[Asteroid] = []
        self.explosions: list[Explosion] = []
        self.lasers = []
        self.torpedoes = []
        self.score = 0
        self.spawn_timer = 0
        self.dead = False
        self.warning_text: Optional[str] = None
        self.background.notify_score_anchor(0)

    def _create_player(self, ship_name: str):
        images = {
            "xwing": (XWing, "x_wing_img"),
            "milleniumfalcon": (MillenniumFalcon, "millennium_falcon_img"),
            "tiefighter": (Tiefighter, "tie_fighter_img"),
            "battledroid": (BattleDroid, "battle_droid_img"),
        }
        cls, asset_key = images.get(ship_name, images["xwing"])
        return cls(
            self.width,
            self.height,
            self.assets[asset_key],
            self.assets.get("torpedo_img"),
        )

    @property
    def system_name(self) -> str:
        return self.background.get_current_system_name()

    def resize(self, width: int, height: int) -> None:
        self.width = max(320, int(width))
        self.height = max(360, int(height))
        self.player.resize(self.width, self.height)
        self.enemy_manager.resize(self.width, self.height)
        self.background.resize(self.width, self.height)
        for asteroid in self.asteroids:
            asteroid.resize(self.width, self.height)
        for explosion in self.explosions:
            explosion.resize(self.height)

    def _create_asteroid(self):
        images = self.assets.get("asteroid_images") or []
        if not images:
            return None
        asteroid = Asteroid(self.width, self.height, images)
        difficulty = self.background.get_current_difficulty()
        profile = DIFFICULTY_SETTINGS[self.config.difficulty]
        bonus = float(difficulty.get("system_bonus", 0.0))
        speed_mul = float(difficulty.get("asteroid_speed_multiplier", 1.0)) * profile["asteroid_speed"] * (1.0 + bonus * 0.70)
        size_mul = profile["asteroid_size"] * (1.0 + bonus * 0.18)
        asteroid.speed = max(1, int(round(asteroid.speed * speed_mul)))
        asteroid.scale *= size_mul
        asteroid.image = pygame.transform.scale_by(
            asteroid.asteroid_images[asteroid.frame],
            asteroid.scale * (self.height / 600),
        )
        asteroid.width, asteroid.height = asteroid.image.get_size()
        asteroid.x = max(0, min(asteroid.x, self.width - asteroid.width))
        return asteroid

    @staticmethod
    def _destroy_asteroid(asteroid, explosions, explosion_img, height):
        explosions.append(
            Explosion(
                asteroid.x + asteroid.width // 2,
                asteroid.y + asteroid.height // 2,
                asteroid.scale,
                explosion_img,
                height,
            )
        )

    def update(self, dt: float, controls: dict[str, bool]) -> None:
        if self.dead:
            return

        if controls.get("left"):
            self.player.move_left()
        if controls.get("right"):
            self.player.move_right(self.width)

        if controls.get("laser"):
            new_lasers = self.player.shoot()
            if new_lasers:
                self.lasers.extend(new_lasers)
        if controls.get("torpedo"):
            torpedo = self.player.torpedo()
            if torpedo:
                self.torpedoes.append(torpedo)

        for laser in self.lasers[:]:
            laser.update()
            if laser.rect.bottom < 0:
                self.lasers.remove(laser)
        for torpedo in self.torpedoes[:]:
            torpedo.update()
            if torpedo.rect.bottom < 0:
                self.torpedoes.remove(torpedo)

        difficulty = self.background.get_current_difficulty()
        system_index = int(difficulty.get("system_index", 0))
        bonus = float(difficulty.get("system_bonus", 0.0))
        profile = DIFFICULTY_SETTINGS[self.config.difficulty]
        density = profile["asteroid_density"] * (1.0 + bonus * 0.80)
        interval = max(ASTEROID_MIN_SPAWN_INTERVAL, int(ASTEROID_SPAWN_INTERVAL / max(0.35, density)))
        self.spawn_timer += 1
        if self.spawn_timer >= interval:
            asteroid = self._create_asteroid()
            if asteroid is not None:
                self.asteroids.append(asteroid)
            self.spawn_timer = 0

        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.y > self.height:
                self.asteroids.remove(asteroid)

        for asteroid in self.asteroids[:]:
            hit_projectile = None
            rect = asteroid.get_rect()
            for projectile in self.lasers[:]:
                if rect.colliderect(projectile.rect):
                    hit_projectile = projectile
                    break
            if hit_projectile is None:
                for projectile in self.torpedoes[:]:
                    if rect.colliderect(projectile.rect):
                        hit_projectile = projectile
                        break
            if hit_projectile is not None:
                self.score += asteroid.get_points()
                self._destroy_asteroid(asteroid, self.explosions, self.assets.get("explosion_img"), self.height)
                if asteroid in self.asteroids:
                    self.asteroids.remove(asteroid)
                if hit_projectile in self.lasers:
                    self.lasers.remove(hit_projectile)
                if hit_projectile in self.torpedoes:
                    self.torpedoes.remove(hit_projectile)

        for asteroid in self.asteroids[:]:
            if asteroid.get_rect().colliderect(self.player.hitbox):
                if not self.player.is_invulnerable():
                    died = self.player.take_damage()
                    self._destroy_asteroid(asteroid, self.explosions, self.assets.get("explosion_img"), self.height)
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
        self.warning_text = enemy_result.warning_text
        if enemy_result.player_dead or self.player.lives <= 0:
            self.dead = True

        for explosion in self.explosions[:]:
            if explosion.update():
                self.explosions.remove(explosion)


    def draw_ghost(self, target: pygame.Surface, other_world: "PointsFightWorld") -> None:
        """Draw only a visual ghost of another local player's ship.

        This method never creates a gameplay entity and never exposes a hitbox.
        The ghost is rendered from the other world solely as an overlay.
        """
        asset_keys = {
            "xwing": "x_wing_img",
            "milleniumfalcon": "millennium_falcon_img",
            "tiefighter": "tie_fighter_img",
            "battledroid": "battle_droid_img",
        }
        image = self.assets.get(asset_keys.get(other_world.config.ship, "x_wing_img"))
        if image is None:
            return
        ghost = pygame.transform.scale_by(image, {
            "xwing": 0.20,
            "milleniumfalcon": 0.75,
            "tiefighter": 0.30,
            "battledroid": 0.12,
        }.get(other_world.config.ship, 0.20)).convert_alpha()
        ghost.set_alpha(105)
        nx = other_world.player.x / max(1, other_world.width)
        ny = other_world.player.y / max(1, other_world.height)
        rect = ghost.get_rect(center=(int(nx * self.width + ghost.get_width() / 2), int(ny * self.height + ghost.get_height() / 2)))
        target.blit(ghost, rect)
        font = pygame.font.Font(None, 22)
        label = font.render(f"{other_world.config.name} • {other_world.score} • {other_world.system_name}", True, (190, 220, 240))
        label.set_alpha(175)
        target.blit(label, label.get_rect(center=(rect.centerx, rect.bottom + 12)))

    def draw(self, target: pygame.Surface) -> None:
        target.fill(BLACK)
        self.background.update(self.score)
        self.background.draw(target)
        for asteroid in self.asteroids:
            asteroid.draw(target)
        self.enemy_manager.draw(target, show_hitboxes=getattr(self.player, "show_hitbox", False))
        for laser in self.lasers:
            laser.draw(target)
        for torpedo in self.torpedoes:
            torpedo.draw(target)
        for explosion in self.explosions:
            explosion.draw(target)
        self.player.draw(target)


class LocalPointsFightSession:
    """Two isolated single-player worlds rendered side-by-side on one PC."""

    def __init__(self, configs: list[PointsPlayerConfig], assets: dict):
        if len(configs) != 2:
            raise ValueError("Lokaler Punktekampf benötigt genau zwei Spieler.")
        self.configs = configs
        self.assets = assets
        self.worlds: list[PointsFightWorld] = []
        self.result = None
        self.show_scoreboard = False

    def _make_worlds(self, width: int, height: int) -> None:
        half = max(320, width // 2)
        self.worlds = [PointsFightWorld(cfg, self.assets, half, height) for cfg in self.configs]

    def run(self, screen: pygame.Surface, clock: pygame.time.Clock) -> dict:
        self._make_worlds(*screen.get_size())
        running = True
        match_start = pygame.time.get_ticks()
        self._match_start = match_start
        duration_ms = 180_000

        controls = [
            {"left": False, "right": False, "laser": False, "torpedo": False},
            {"left": False, "right": False, "laser": False, "torpedo": False},
        ]

        while running:
            dt = min(0.05, clock.tick(60) / 1000.0)
            width, height = screen.get_size()
            half = max(320, width // 2)
            if not self.worlds or self.worlds[0].width != half or self.worlds[0].height != height:
                self._make_worlds(width, height)

            for state in controls:
                state["laser"] = False
                state["torpedo"] = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((max(640, event.w), max(360, event.h)), pygame.RESIZABLE)
                    self._make_worlds(*screen.get_size())
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return {"quit": True}
                    if event.key == pygame.K_TAB:
                        self.show_scoreboard = True
                    if event.key == pygame.K_w:
                        controls[0]["laser"] = True
                    if event.key == pygame.K_s:
                        controls[0]["torpedo"] = True
                    if event.key == pygame.K_UP:
                        controls[1]["laser"] = True
                    if event.key == pygame.K_DOWN:
                        controls[1]["torpedo"] = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_TAB:
                    self.show_scoreboard = False

            keys = pygame.key.get_pressed()
            controls[0]["left"] = keys[pygame.K_a]
            controls[0]["right"] = keys[pygame.K_d]
            controls[1]["left"] = keys[pygame.K_LEFT]
            controls[1]["right"] = keys[pygame.K_RIGHT]

            for world, state in zip(self.worlds, controls):
                world.update(dt, state)

            surfaces = [pygame.Surface((half, height), pygame.SRCALPHA), pygame.Surface((width - half, height), pygame.SRCALPHA)]
            for surface, world in zip(surfaces, self.worlds):
                world.draw(surface)
            # Ghosts are drawn only after the local world is rendered.  They are
            # never inserted into either world's collision/update lists.
            self.worlds[0].draw_ghost(surfaces[0], self.worlds[1])
            self.worlds[1].draw_ghost(surfaces[1], self.worlds[0])

            screen.fill((0, 0, 0))
            screen.blit(surfaces[0], (0, 0))
            screen.blit(surfaces[1], (half, 0))
            pygame.draw.line(screen, (90, 100, 125), (half, 0), (half, height), 2)

            self._draw_hud(screen, half, height)

            if self.show_scoreboard:
                self._draw_scoreboard(screen)

            elapsed = pygame.time.get_ticks() - match_start
            if elapsed >= duration_ms or all(world.dead for world in self.worlds):
                self.result = sorted(
                    [{"name": w.config.name, "score": w.score, "system": w.system_name} for w in self.worlds],
                    key=lambda x: x["score"],
                    reverse=True,
                )
                running = False

            pygame.display.flip()

        return {"result": self.result, "quit": False}

    def _draw_hud(self, screen, half, height):
        font = pygame.font.Font(None, max(22, int(height * 0.035)))
        for i, world in enumerate(self.worlds):
            x = i * half + 10
            screen.blit(font.render(f"{world.config.name}  •  {world.score} Punkte", True, (235, 240, 250)), (x, 10))
            screen.blit(font.render(world.system_name, True, (180, 195, 215)), (x, 38))
            saber_key = "lightsaber_blue_img" if world.config.faction == "rebels" else "lightsaber_red_img"
            saber = self.assets.get(saber_key)
            if saber is not None:
                target_h = 18
                target_w = max(35, int(saber.get_width() * target_h / saber.get_height()))
                icon = pygame.transform.smoothscale(saber, (target_w, target_h))
                for life_index in range(max(0, world.player.lives)):
                    screen.blit(icon, (x + life_index * (target_w + 4), 66))
            if world.dead:
                text = font.render("GAME OVER", True, (255, 130, 130))
                screen.blit(text, text.get_rect(center=(i * half + half // 2, height // 2)))

        remaining = max(0, 180_000 - (pygame.time.get_ticks() - getattr(self, "_match_start", pygame.time.get_ticks())))
        font = pygame.font.Font(None, 28)
        timer = font.render(f"{remaining // 60000:02d}:{(remaining % 60000) // 1000:02d}", True, (255, 255, 255))
        screen.blit(timer, timer.get_rect(center=(screen.get_width() // 2, 24)))

    def _draw_scoreboard(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 34)
        title = font.render("PUNKTEKAMPF – RANGLISTE", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 70)))
        rows = sorted(self.worlds, key=lambda w: w.score, reverse=True)
        for index, world in enumerate(rows, 1):
            text = f"{index}.  {world.config.name}   {world.score}   {world.system_name}"
            surface = font.render(text, True, (230, 235, 245))
            screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, 125 + index * 42)))
