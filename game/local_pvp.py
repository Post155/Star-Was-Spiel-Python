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