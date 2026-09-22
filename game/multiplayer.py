"""High-level multiplayer state and remote-player rendering."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional

import pygame

from game.constants import (
    SHIP_SCALE_BATTLEDROID,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_XWING,
)
from game.network import LANClient, LANServer, LAN_PORT, MAX_PLAYERS

SHIP_SCALES = {
    "xwing": SHIP_SCALE_XWING,
    "milleniumfalcon": SHIP_SCALE_MILLENNIUM,
    "tiefighter": SHIP_SCALE_TIEFIGHTER,
    "battledroid": SHIP_SCALE_BATTLEDROID,
}

SHIP_ASSET_KEYS = {
    "xwing": "x_wing_img",
    "milleniumfalcon": "millennium_falcon_img",
    "tiefighter": "tie_fighter_img",
    "battledroid": "battle_droid_img",
}


@dataclass
class RemotePlayer:
    player_id: str
    name: str
    ship: str = "xwing"
    x: float = 0.0
    y: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0
    source_width: int = 800
    source_height: int = 600
    score: int = 0
    lives: int = 3
    alive: bool = True
    connected: bool = True
    ready: bool = False
    last_update: float = field(default_factory=time.monotonic)

    def update_from_dict(self, data: dict, local_width: int, local_height: int) -> None:
        self.name = str(data.get("name") or self.name)[:20]
        self.ship = str(data.get("ship") or self.ship)
        self.source_width = max(320, int(data.get("width", self.source_width) or self.source_width))
        self.source_height = max(240, int(data.get("height", self.source_height) or self.source_height))
        raw_x = float(data.get("x", 0.0) or 0.0)
        raw_y = float(data.get("y", 0.0) or 0.0)
        self.target_x = raw_x / self.source_width * max(1, local_width)
        self.target_y = raw_y / self.source_height * max(1, local_height)
        self.score = max(0, int(data.get("score", self.score) or 0))
        self.lives = max(0, int(data.get("lives", self.lives) or 0))
        self.alive = bool(data.get("alive", self.alive))
        self.connected = bool(data.get("connected", True))
        self.ready = bool(data.get("ready", False))
        self.last_update = time.monotonic()

    def interpolate(self, factor: float = 0.28) -> None:
        self.x += (self.target_x - self.x) * factor
        self.y += (self.target_y - self.y) * factor


class MultiplayerSession:
    """Owns one LAN server/client pair and the remote-player cache."""

    def __init__(self, debug: bool = True, game_mode: str = "lan", max_players: int = MAX_PLAYERS):
        self.debug = debug
        self.game_mode = str(game_mode or "lan")
        self.max_players = max(1, min(MAX_PLAYERS, int(max_players)))
        self.server: Optional[LANServer] = None
        self.client = LANClient(debug=debug)
        self.remote_players: Dict[str, RemotePlayer] = {}
        self.local_name = "Spieler"
        self.local_ship = "xwing"
        self.local_score = 0
        self.local_lives = 3
        self.local_alive = True
        self._last_state_send = 0.0
        self._last_width = 800
        self._last_height = 600
        self.error: Optional[str] = None
        self.hosting = False

    @property
    def local_id(self) -> Optional[str]:
        return self.client.player_id

    @property
    def connected(self) -> bool:
        return self.client.connected

    @property
    def connecting(self) -> bool:
        return self.client.connecting

    @property
    def phase(self) -> str:
        return self.client.phase

    @property
    def host_id(self) -> Optional[str]:
        return self.client.host_id

    @property
    def players(self) -> Dict[str, dict]:
        return self.client.players

    def host(self, name: str, port: int = LAN_PORT) -> None:
        self.local_name = name.strip() or "Host"
        self.server = LANServer(port=port, debug=self.debug, game_mode=self.game_mode, max_players=self.max_players)
        self.server.start()
        self.hosting = True
        # The host is a normal client too.  This keeps all lobby/game paths identical.
        self.client.connect_async("127.0.0.1", port, self.local_name, game_mode=self.game_mode)

    def join(self, host: str, name: str, port: int = LAN_PORT) -> None:
        self.local_name = name.strip() or "Spieler"
        self.hosting = False
        self.client.connect_async(host, port, self.local_name, game_mode=self.game_mode)

    def request_start(self) -> None:
        self.client.request_start()

    def poll(self, width: int = 800, height: int = 600) -> list[dict]:
        events = self.client.poll()
        if self.client.error:
            self.error = self.client.error
        raw_players = self.client.players
        local_id = self.local_id
        seen = set()

        for player_id, data in raw_players.items():
            if player_id == local_id:
                continue
            seen.add(player_id)
            remote = self.remote_players.get(player_id)
            if remote is None:
                remote = RemotePlayer(
                    player_id=player_id,
                    name=str(data.get("name") or "Spieler"),
                )
                remote.x = width * 0.5
                remote.y = height * 0.35
                self.remote_players[player_id] = remote
            remote.update_from_dict(data, width, height)
            remote.interpolate()

        for player_id in list(self.remote_players):
            if player_id not in seen:
                self.remote_players.pop(player_id, None)

        return events

    def send_ready(self, ship: str, difficulty: str, game_rule: Optional[str] = None) -> None:
        self.local_ship = ship
        self.client.send_ready(self.local_name, ship, difficulty, game_rule=game_rule)

    def update_local_state(self, player, ship: str, score: int, width: int, height: int) -> None:
        self.local_ship = ship
        self.local_score = int(score)
        self.local_lives = int(getattr(player, "lives", 0))
        self.local_alive = self.local_lives > 0
        now = time.monotonic()
        if now - self._last_state_send < 0.05:
            return
        self._last_state_send = now
        self._last_width = width
        self._last_height = height
        self.client.send_state(
            x=float(getattr(player, "x", 0.0)),
            y=float(getattr(player, "y", 0.0)),
            width=width,
            height=height,
            ship=ship,
            score=self.local_score,
            lives=self.local_lives,
            alive=self.local_alive,
        )

    def set_final_local_state(self, player, ship: str, score: int, width: int, height: int) -> None:
        self.local_ship = ship
        self.local_score = int(score)
        self.local_lives = int(getattr(player, "lives", 0))
        self.local_alive = self.local_lives > 0
        self.client.send_state(
            x=float(getattr(player, "x", 0.0)),
            y=float(getattr(player, "y", 0.0)),
            width=width,
            height=height,
            ship=ship,
            score=self.local_score,
            lives=self.local_lives,
            alive=self.local_alive,
        )

    def is_host(self) -> bool:
        return bool(self.local_id and self.local_id == self.host_id)

    def get_scoreboard_rows(self) -> list[dict]:
        rows = []
        for player_id, player in self.client.players.items():
            row = dict(player)
            row["id"] = player_id
            rows.append(row)
        if self.local_id and self.local_id not in {row["id"] for row in rows}:
            rows.append({
                "id": self.local_id,
                "name": self.local_name,
                "score": self.local_score,
                "alive": self.local_alive,
                "ship": self.local_ship,
                "lives": self.local_lives,
            })
        rows.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
        return rows

    def draw_remote_players(self, screen: pygame.Surface, assets: dict) -> None:
        for remote in self.remote_players.values():
            asset_key = SHIP_ASSET_KEYS.get(remote.ship)
            image = assets.get(asset_key) if asset_key else None
            if image is None:
                continue
            scale = SHIP_SCALES.get(remote.ship, 0.20)
            ghost = pygame.transform.scale_by(image, scale).convert_alpha()
            ghost.set_alpha(125 if remote.alive else 55)
            rect = ghost.get_rect(center=(int(remote.x + ghost.get_width() / 2), int(remote.y + ghost.get_height() / 2)))

            # A lightweight glow/outline without altering the original sprite.
            glow = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (120, 210, 255, 45 if remote.alive else 20), glow.get_rect(), 3)
            screen.blit(glow, (rect.x - 8, rect.y - 8))
            screen.blit(ghost, rect)

            font = pygame.font.Font(None, 24)
            label_text = remote.name if remote.alive else f"{remote.name} – GAME OVER"
            label = font.render(label_text, True, (230, 245, 255))
            label.set_alpha(220 if remote.alive else 150)
            label_rect = label.get_rect(center=(rect.centerx, rect.top - 10))
            screen.blit(label, label_rect)

    def stop(self, graceful: bool = True) -> None:
        self.client.disconnect(graceful=graceful)
        if self.server is not None:
            self.server.stop(reason="Der Host hat das Spiel beendet.")
            self.server = None
        self.remote_players.clear()
        self.hosting = False
