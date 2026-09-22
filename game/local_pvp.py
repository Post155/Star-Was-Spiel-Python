"""Local two-player PvP mode.

Reuses the authoritative PvP world from game.pvp_duel.py.  The only things
that differ from LAN PvP are the transport/session adapter and the keyboard
input source.  No socket is created in this mode.
"""
from __future__ import annotations

from typing import Dict, List

import pygame

from game.constants import (
    LOCAL_PVP_PLAYER1_NAME,
    LOCAL_PVP_PLAYER2_NAME,
    PVP_SCORE_LIMIT_MS,
)
from game.pvp_duel import PvPDuelSession, SHIP_ASSET_KEYS
from game.pvp_input import LocalPvPInput


class LocalPvPTransport:
    """Minimal session adapter so PvPDuelSession can run without networking."""

    def __init__(self, player1: Dict[str, str], player2: Dict[str, str], game_rule: str) -> None:
        self.host_id = "local_p1"
        self.local_id = "local_p1"
        self.phase = "game"
        self.connected = True
        self.server = None
        self.client = None
        self.players = {
            "local_p1": {
                "id": "local_p1",
                "name": str(player1.get("name") or LOCAL_PVP_PLAYER1_NAME)[:20],
                "ship": str(player1.get("ship") or "xwing"),
                "game_rule": game_rule,
            },
            "local_p2": {
                "id": "local_p2",
                "name": str(player2.get("name") or LOCAL_PVP_PLAYER2_NAME)[:20],
                "ship": str(player2.get("ship") or "tiefighter"),
                "game_rule": game_rule,
            },
        }

    def is_host(self) -> bool:
        return True

    def stop(self) -> None:
        self.connected = False


class LocalPvPDuelSession(PvPDuelSession):
    """PvP duel on one computer using two simultaneous local input channels."""

    def __init__(self, player1: Dict[str, str], player2: Dict[str, str], assets: dict, mode: str) -> None:
        transport = LocalPvPTransport(player1, player2, mode)
        super().__init__(transport, assets, mode=mode, debug=False)
        self.local_transport = transport
        self.local_input = LocalPvPInput()
        self.local_input_states = {
            "local_p1": {"left": False, "right": False},
            "local_p2": {"left": False, "right": False},
        }
        self.local_fire_events: List[tuple[str, str]] = []
        self.local_player_ids = ("local_p1", "local_p2")

    def _process_host_inputs(self, local_left: bool, local_right: bool) -> None:
        """Apply both local players' movement and fire events.

        ``LocalPvPInput`` uses the public binding names ``player1`` and
        ``player2`` while the PvP session internally uses ``local_p1`` and
        ``local_p2``.  Keep that translation here so the local input module
        stays independent from the PvP session/network naming.
        """
        for player_id in self.local_player_ids:
            duel_player = self.players.get(player_id)
            if duel_player is None:
                continue
            state = self.local_input_states.get(player_id, {})
            self._move_player(
                duel_player,
                bool(state.get("left", False)),
                bool(state.get("right", False)),
            )

        for player_id, weapon in self.local_fire_events:
            self._fire_weapon_host(player_id, weapon)

        self.local_fire_events.clear()

    def _draw_local_world(self, screen: pygame.Surface) -> None:
        """Render the shared world with both ships fully visible."""
        if self.background is not None:
            self.background.draw(screen)

        sx = screen.get_width() / max(1, self.source_width)
        sy = screen.get_height() / max(1, self.source_height)
        images = self.assets.get("asteroid_images", [])

        for asteroid in self.asteroids.values():
            image = images[asteroid.frame % len(images)] if images else asteroid.image
            target = pygame.transform.smoothscale(
                image,
                (max(2, int(asteroid.width * sx)), max(2, int(asteroid.height * sy))),
            )
            screen.blit(target, (int(asteroid.x * sx), int(asteroid.y * sy)))

        for projectile in self.projectiles:
            rect = projectile.obj.rect
            px = rect.x * sx
            py = rect.y * sy
            pw = max(2, int(rect.width * sx))
            ph = max(2, int(rect.height * sy))
            if projectile.weapon == "torpedo" and getattr(projectile.obj, "image", None) is not None:
                image = pygame.transform.smoothscale(projectile.obj.image, (pw, ph))
                if projectile.owner_id == "local_p2":
                    image = pygame.transform.flip(image, False, True)
                screen.blit(image, (int(px), int(py)))
            else:
                pygame.draw.rect(screen, (255, 70, 70), pygame.Rect(int(px), int(py), pw, ph))

        for player in self.players.values():
            image = self.assets.get(SHIP_ASSET_KEYS.get(player.ship_name))
            if image is None:
                continue

            alive = not player.eliminated and player.respawn_at <= 0.0 and player.ship.lives > 0
            if not alive:
                label = f"{player.name} – GAME OVER" if player.eliminated else f"{player.name} – RESPAWN"
                dummy = pygame.Rect(int(player.ship.x * sx), int(player.ship.y * sy), max(2, int(player.ship.width * sx)), max(2, int(player.ship.height * sy)))
                self._draw_label(screen, dummy, label, 165)
                continue

            alpha = 255
            if player.ship.is_invulnerable():
                alpha = 190

            rect = self._draw_ship_surface(
                screen,
                image,
                player.ship.x,
                player.ship.y,
                player.ship.width,
                player.ship.height,
                player.role,
                "bottom",
                alpha=alpha,
            )
            self._draw_label(screen, rect, player.name, 255)

        for effect in self.effects.values():
            self._draw_effect(screen, effect, "bottom")

    def draw_world(self, screen: pygame.Surface) -> None:
        self._draw_local_world(screen)

    def draw_hud(self, screen: pygame.Surface) -> None:
        width, height = screen.get_size()
        font = pygame.font.Font(None, max(22, int(height * 0.032)))
        small_font = pygame.font.Font(None, max(19, int(height * 0.025)))

        p1 = self.players.get("local_p1")
        p2 = self.players.get("local_p2")
        if p1 is None or p2 is None:
            return

        mode_text = "LETZTER ÜBERLEBENDER" if self.mode == "last_survivor" else "PUNKTEKAMPF"
        left_text = f"P1 {p1.name}: {p1.score} Punkte • Leben {p1.ship.lives}"
        right_text = f"P2 {p2.name}: {p2.score} Punkte • Leben {p2.ship.lives}"
        screen.blit(font.render(left_text, True, (130, 220, 255)), (10, 10))
        right_surface = font.render(right_text, True, (255, 180, 180))
        screen.blit(right_surface, (width - right_surface.get_width() - 10, 10))

        if self.mode == "points":
            remaining = max(0, PVP_SCORE_LIMIT_MS - self.match_elapsed_ms)
            timer = f"{remaining // 60000:02d}:{(remaining % 60000) // 1000:02d}"
            timer_surface = font.render(f"{mode_text} • {timer}", True, (255, 255, 255))
        else:
            timer_surface = font.render(mode_text, True, (255, 255, 255))
        screen.blit(timer_surface, timer_surface.get_rect(center=(width // 2, 18)))

        controls = small_font.render(LocalPvPInput.control_text(), True, (175, 185, 205))
        screen.blit(controls, controls.get_rect(center=(width // 2, height - 18)))

    def run(self, screen, clock) -> dict:
        running = True
        self.local_input.reset()

        while running:
            dt = min(0.05, clock.tick(60) / 1000.0)
            width, height = screen.get_size()
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.VIDEORESIZE:
                    width = max(480, event.w)
                    height = max(360, event.h)
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                    continue
                self.local_input.process_event(event)

            if self.local_input.quit_requested:
                return {"quit": True}

            raw_states = self.local_input.get_states()
            self.local_input_states = {
                "local_p1": dict(raw_states.get("player1", {"left": False, "right": False})),
                "local_p2": dict(raw_states.get("player2", {"left": False, "right": False})),
            }

            for player_id, weapon in self.local_input.consume_fire_events():
                internal_id = {
                    "player1": "local_p1",
                    "player2": "local_p2",
                }.get(player_id)
                if internal_id is not None:
                    self.local_fire_events.append((internal_id, weapon))

            self.update_host(
                bool(self.local_input_states["local_p1"]["left"]),
                bool(self.local_input_states["local_p1"]["right"]),
                dt,
                width,
                height,
                [],
            )

            screen.fill((0, 0, 0))
            self.draw_world(screen)
            self.draw_hud(screen)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_TAB] and not self.match_over:
                self.draw_scoreboard(screen)

            if self.match_over:
                self._draw_result_screen(screen)
                if pygame.key.get_pressed()[pygame.K_RETURN] or pygame.key.get_pressed()[pygame.K_ESCAPE] or pygame.key.get_pressed()[pygame.K_SPACE]:
                    return {"result": self.result}

            pygame.display.flip()

        return {"result": self.result}

class LocalPointsFightSession:
    """Two independent single-player worlds sharing one local score match."""

    def __init__(self, player1: Dict[str, str], player2: Dict[str, str], assets: dict, difficulty: str = "normal"):
        from game.points_fight import PointFightWorld
        self.PointFightWorld = PointFightWorld
        self.assets = assets
        self.player1 = player1
        self.player2 = player2
        self.difficulty = difficulty
        self.worlds = []
        self.match_started_at = 0.0
        self.match_over = False
        self.result = None

    def _new_worlds(self, width, height):
        half_h = max(360, height // 2 - 4)
        self.worlds = [
            self.PointFightWorld(width, half_h, self.assets, self.player1["ship"], self.difficulty),
            self.PointFightWorld(width, half_h, self.assets, self.player2["ship"], self.difficulty),
        ]
        self.match_started_at = pygame.time.get_ticks()

    def _draw_lives(self, surface, lives, faction, x=8, y=30):
        key = "lightsaber_blue_img" if faction == "rebels" else "lightsaber_red_img"
        image = self.assets.get(key)
        if image is None:
            return
        target_h = 20
        scale = target_h / max(1, image.get_height())
        saber = pygame.transform.smoothscale(
            image, (max(45, int(image.get_width() * scale)), target_h)
        )
        for index in range(max(0, int(lives))):
            surface.blit(saber, (x, y + index * (target_h + 5)))

    def _draw_world_panel(self, screen, world, name, faction, y_offset, player_number, warning=True):
        panel_h = screen.get_height() // 2
        view = screen.subsurface(pygame.Rect(0, y_offset, screen.get_width(), panel_h)).copy()
        world.draw(view)
        font = pygame.font.Font(None, max(24, int(panel_h * 0.055)))
        small = pygame.font.Font(None, max(20, int(panel_h * 0.040)))
        header = f"P{player_number} {name}  •  {world.score} Punkte  •  {world.system_name}"
        screen.blit(font.render(header, True, (255, 255, 255)), (10, y_offset + 8))
        self._draw_lives(screen, world.lives, faction, 8, y_offset + 42)
        if warning and world.warning_text and not world.dead:
            overlay = pygame.Surface((screen.get_width(), panel_h), pygame.SRCALPHA)
            overlay.fill((120, 0, 0, 75))
            screen.blit(overlay, (0, y_offset))
            msg = small.render(world.warning_text, True, (255, 235, 150))
            screen.blit(msg, msg.get_rect(center=(screen.get_width() // 2, y_offset + panel_h // 2)))
        if world.dead:
            dead = font.render("GAME OVER", True, (255, 120, 120))
            screen.blit(dead, dead.get_rect(center=(screen.get_width() // 2, y_offset + panel_h // 2)))

    def _draw_result(self, screen):
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, max(48, int(height * 0.09)))
        small = pygame.font.Font(None, max(24, int(height * 0.038)))
        p1, p2 = self.worlds
        if p1.score > p2.score:
            title = f"SIEGER: {self.player1['name']}"
        elif p2.score > p1.score:
            title = f"SIEGER: {self.player2['name']}"
        else:
            title = "UNENTSCHIEDEN"
        screen.blit(font.render(title, True, (255, 235, 150)), (width // 2 - font.size(title)[0] // 2, height // 3))
        detail = f"{self.player1['name']}: {p1.score}   •   {self.player2['name']}: {p2.score}"
        screen.blit(small.render(detail, True, (230, 235, 245)), (width // 2 - small.size(detail)[0] // 2, height // 2))
        hint = small.render("ENTER / LEERTASTE / ESC = zurück zum Menü", True, (170, 180, 195))
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 35)))

    def run(self, screen, clock) -> dict:
        self._new_worlds(*screen.get_size())
        running = True
        while running:
            dt = min(0.05, clock.tick(60) / 1000.0)
            width, height = screen.get_size()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.VIDEORESIZE:
                    width = max(480, event.w)
                    height = max(720, event.h)
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                    self._new_worlds(width, height)
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.match_over:
                    return {"result": self.result}

            keys = pygame.key.get_pressed()
            elapsed = pygame.time.get_ticks() - self.match_started_at
            time_up = elapsed >= PVP_SCORE_LIMIT_MS

            if not self.match_over:
                self.worlds[0].move(keys[pygame.K_a], keys[pygame.K_d])
                self.worlds[1].move(keys[pygame.K_LEFT], keys[pygame.K_RIGHT])
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_w, pygame.K_SPACE):
                            self.worlds[0].shoot("laser")
                        elif event.key == pygame.K_s:
                            self.worlds[0].shoot("torpedo")
                        elif event.key == pygame.K_UP:
                            self.worlds[1].shoot("laser")
                        elif event.key == pygame.K_DOWN:
                            self.worlds[1].shoot("torpedo")
                self.worlds[0].update(dt)
                self.worlds[1].update(dt)
                if time_up:
                    self.match_over = True
                    self.result = {"mode": "points"}

            screen.fill((0, 0, 0))
            half = height // 2
            self._draw_world_panel(screen, self.worlds[0], self.player1["name"], self.player1.get("faction", "rebels"), 0, 1)
            pygame.draw.line(screen, (120, 210, 255), (0, half), (width, half), 2)
            self._draw_world_panel(screen, self.worlds[1], self.player2["name"], self.player2.get("faction", "empire"), half, 2)

            remaining = max(0, PVP_SCORE_LIMIT_MS - elapsed)
            timer = pygame.font.Font(None, max(24, int(height * 0.035))).render(
                f"PUNKTEKAMPF  •  {remaining // 60000:02d}:{(remaining % 60000) // 1000:02d}",
                True, (255, 255, 255)
            )
            screen.blit(timer, timer.get_rect(center=(width // 2, height // 2)))

            from game.scoreboard import draw_scoreboard, draw_live_ranking
            rows = [
                {"id": "local_p1", "name": self.player1["name"], "score": self.worlds[0].score, "alive": not self.worlds[0].dead, "system_name": self.worlds[0].system_name, "system_index": self.worlds[0].system_index},
                {"id": "local_p2", "name": self.player2["name"], "score": self.worlds[1].score, "alive": not self.worlds[1].dead, "system_name": self.worlds[1].system_name, "system_index": self.worlds[1].system_index},
            ]
            rows.sort(key=lambda row: int(row["score"]), reverse=True)
            draw_live_ranking(screen, rows, "local_p1")
            if pygame.key.get_pressed()[pygame.K_TAB] and not self.match_over:
                draw_scoreboard(screen, rows, "local_p1")

            if self.match_over:
                self._draw_result(screen)
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_RETURN] or pressed[pygame.K_SPACE] or pressed[pygame.K_ESCAPE]:
                    return {"result": self.result}

            pygame.display.flip()
        return {"result": self.result}
