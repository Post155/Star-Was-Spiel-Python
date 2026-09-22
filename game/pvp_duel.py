"""Authoritative two-player LAN PvP duel.

The normal LAN multiplayer mode remains a lightweight state/ghost system.
PvP-Duell deliberately uses a different model: the host process owns the
shared simulation (players, projectiles, asteroids, collisions, scoring and
system transitions). Clients send only movement/fire input and render the
host snapshots. This keeps both machines on the same world without making
Pygame wait for network traffic.
"""
from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pygame

from game.background import BackgroundManager
from game.constants import (
    ASTEROID_MIN_SPAWN_INTERVAL,
    DEFAULT_DIFFICULTY,
    DIFFICULTY_SETTINGS,
    PVP_ASTEROID_BASE_SPAWN_INTERVAL,
    PVP_ASTEROID_MIN_SPAWN_INTERVAL,
    PVP_ASTEROID_PLAYER_SAFE_DISTANCE,
    PVP_ASTEROID_SPAWN_ATTEMPTS,
    PVP_ASTEROID_SPAWN_MAX_Y_RATIO,
    PVP_ASTEROID_SPAWN_MIN_Y,
    PVP_DEFAULT_MODE,
    PVP_EXPLOSION_DURATION_MS,
    PVP_HIT_SCORE,
    PVP_INPUT_INTERVAL_MS,
    PVP_KILL_SCORE,
    PVP_LASER_DAMAGE,
    PVP_PLAYER_SPEED,
    PVP_TORPEDO_DAMAGE,
    PVP_MAX_PLAYERS,
    PVP_MAX_PROJECTILES,
    PVP_PLAYER_BOTTOM_MARGIN,
    PVP_PLAYER_HORIZONTAL_PADDING,
    PVP_PLAYER_TOP_MARGIN,
    PVP_RESPAWN_DELAY_MS,
    PVP_RESPAWN_INVULNERABILITY_MS,
    PVP_RESULT_DELAY_MS,
    PVP_SCORE_LIMIT_MS,
    PVP_SNAPSHOT_INTERVAL_MS,
)
from game.entities.asteroid import Asteroid
from game.entities.explosion import Explosion
from game.entities.projectiles import Laser, Torpedo
from game.entities.ships import BattleDroid, MillenniumFalcon, Tiefighter, XWing


SHIP_ASSET_KEYS = {
    "xwing": "x_wing_img",
    "milleniumfalcon": "millennium_falcon_img",
    "tiefighter": "tie_fighter_img",
    "battledroid": "battle_droid_img",
}

SHIP_CLASSES = {
    "xwing": XWing,
    "milleniumfalcon": MillenniumFalcon,
    "tiefighter": Tiefighter,
    "battledroid": BattleDroid,
}

WEAPON_DAMAGE = {
    "laser": PVP_LASER_DAMAGE,
    "torpedo": PVP_TORPEDO_DAMAGE,
}


@dataclass
class DuelStats:
    shots_fired: int = 0
    hits: int = 0
    kills: int = 0
    damage_dealt: int = 0
    survival_time_ms: int = 0

    @property
    def accuracy(self) -> float:
        if self.shots_fired <= 0:
            return 0.0
        return (self.hits / self.shots_fired) * 100.0


@dataclass
class DuelPlayer:
    player_id: str
    name: str
    ship_name: str
    role: str
    ship: object
    stats: DuelStats = field(default_factory=DuelStats)
    score: int = 0
    respawn_at: float = 0.0
    alive_since: float = 0.0
    eliminated: bool = False
    last_input_left: bool = False
    last_input_right: bool = False
    x_target: float = 0.0
    role_index: int = 0

    def reset_spawn(self, width: int, height: int, now: float, invulnerable_ms: int = 0) -> None:
        self.ship.x = width // 2 - self.ship.width // 2
        if self.role == "bottom":
            self.ship.y = height - self.ship.height - PVP_PLAYER_BOTTOM_MARGIN
        else:
            self.ship.y = PVP_PLAYER_TOP_MARGIN
        self.ship.update_hitbox()
        self.ship.invulnerable_until = pygame.time.get_ticks() + max(0, int(invulnerable_ms))
        self.respawn_at = 0.0
        self.alive_since = now


@dataclass
class DuelProjectile:
    projectile_id: str
    owner_id: str
    weapon: str
    obj: object
    damage: int


@dataclass
class DuelEffect:
    effect_id: str
    x: float
    y: float
    scale: float
    created_at: float
    image: Optional[pygame.Surface] = None


@dataclass
class DuelViewPlayer:
    player_id: str
    name: str
    ship: str
    role: str
    x: float
    y: float
    width: int
    height: int
    score: int
    lives: int
    alive: bool
    eliminated: bool
    kills: int
    hits: int
    shots: int
    damage: int
    survival_ms: int
    invulnerable: bool = False
    target_x: float = 0.0
    target_y: float = 0.0

    def set_target(self, x: float, y: float, factor: float = 0.35) -> None:
        if self.target_x == 0.0 and self.target_y == 0.0 and self.x == 0.0 and self.y == 0.0:
            self.x = x
            self.y = y
        self.target_x = x
        self.target_y = y
        self.x += (self.target_x - self.x) * factor
        self.y += (self.target_y - self.y) * factor


class PvPDuelSession:
    """Run one two-player duel on top of the existing LAN session."""

    def __init__(self, multiplayer_session, assets: dict, mode: str = PVP_DEFAULT_MODE, debug: bool = True):
        self.session = multiplayer_session
        self.assets = assets
        requested_mode = mode if mode in {"last_survivor", "points"} else PVP_DEFAULT_MODE
        host_rule = None
        try:
            if self.session.host_id and self.session.host_id in self.session.players:
                host_rule = self.session.players[self.session.host_id].get("game_rule")
        except Exception:
            host_rule = None
        self.mode = host_rule if host_rule in {"last_survivor", "points"} else requested_mode
        self.debug = debug
        self.is_host = self.session.is_host()
        self.local_id = self.session.local_id

        self.background: Optional[BackgroundManager] = None
        self.players: Dict[str, DuelPlayer] = {}
        self.view_players: Dict[str, DuelViewPlayer] = {}
        self.projectiles: List[DuelProjectile] = []
        self.asteroids: Dict[str, Asteroid] = {}
        self.effects: Dict[str, DuelEffect] = {}
        self.client_effects: Dict[str, DuelEffect] = {}

        self.source_width = 800
        self.source_height = 600
        self._last_snapshot_sent = 0.0
        self._last_input_sent = 0.0
        self._fire_sequence = 0
        self._last_system_order: List[str] = []
        self._last_transition_signature = None
        self._last_seen_effects: set[str] = set()
        self.latest_snapshot: Optional[dict] = None
        self.match_started_at = time.monotonic()
        self.match_elapsed_ms = 0
        self.match_over = False
        self.result = None
        self._result_started_at = 0.0
        self._quit_requested = False
        self._last_frame_time = time.monotonic()
        self._asteroid_spawn_timer = 0
        self._next_effect_cleanup = time.monotonic()

    # ------------------------------------------------------------------
    # Host-side setup / simulation
    # ------------------------------------------------------------------
    def _make_ship(self, ship_name: str, width: int, height: int):
        cls = SHIP_CLASSES.get(ship_name, XWing)
        asset_key = SHIP_ASSET_KEYS.get(ship_name, "x_wing_img")
        image = self.assets.get(asset_key)
        if image is None:
            raise RuntimeError(f"Schiffs-Asset fehlt: {asset_key}")
        return cls(width, height, image, self.assets.get("torpedo_img"))

    def _setup_host_world(self, width: int, height: int) -> bool:
        if self.players:
            return True
        raw_players = list(self.session.players.items())
        if len(raw_players) != PVP_MAX_PLAYERS:
            return False

        self.source_width = max(480, int(width))
        self.source_height = max(360, int(height))
        self.background = BackgroundManager(
            self.source_width,
            self.source_height,
            self.assets,
            auto_switch=True,
        )
        self._last_system_order = [item.id_name for item in self.background.systems.get_all_systems()]
        now = time.monotonic()

        # The host always gets role 1/bottom; the second connected player gets top.
        ordered = sorted(
            raw_players,
            key=lambda item: (0 if str(item[0]) == str(self.session.host_id) else 1, str(item[0])),
        )
        for index, (player_id, data) in enumerate(ordered):
            ship_name = str(data.get("ship") or "xwing")
            player = self._make_ship(ship_name, self.source_width, self.source_height)
            player.speed = PVP_PLAYER_SPEED
            role = "bottom" if index == 0 else "top"
            duel_player = DuelPlayer(
                player_id=str(player_id),
                name=str(data.get("name") or "Spieler")[:20],
                ship_name=ship_name,
                role=role,
                ship=player,
                role_index=index,
            )
            duel_player.reset_spawn(self.source_width, self.source_height, now)
            self.players[duel_player.player_id] = duel_player
        self.match_started_at = time.monotonic()
        self._last_frame_time = self.match_started_at
        return True

    def _spawn_safe_asteroid(self) -> None:
        if self.background is None:
            return
        if len(self.asteroids) >= 36:
            return

        difficulty = self.background.get_current_difficulty()
        system_bonus = float(difficulty.get("system_bonus", 0.0))
        profile = DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY]
        speed_multiplier = (
            float(difficulty.get("asteroid_speed_multiplier", 1.0))
            * profile["asteroid_speed"]
            * (1.0 + system_bonus * 0.70)
        )
        size_multiplier = profile["asteroid_size"] * (1.0 + system_bonus * 0.18)

        asteroid = Asteroid(
            self.source_width,
            self.source_height,
            self.assets.get("asteroid_images", []),
            size_multiplier=size_multiplier,
            speed_multiplier=speed_multiplier,
        )
        if not self.assets.get("asteroid_images"):
            return

        # The Asteroid constructor normally starts above the screen. For PvP the
        # authoritative world intentionally picks a visible safe spawn position.
        for _ in range(PVP_ASTEROID_SPAWN_ATTEMPTS):
            max_y = max(
                PVP_ASTEROID_SPAWN_MIN_Y,
                int(self.source_height * PVP_ASTEROID_SPAWN_MAX_Y_RATIO),
            )
            import random
            x_value = random.randint(
                PVP_PLAYER_HORIZONTAL_PADDING,
                max(PVP_PLAYER_HORIZONTAL_PADDING, self.source_width - asteroid.width - PVP_PLAYER_HORIZONTAL_PADDING),
            )
            y_value = random.randint(
                PVP_ASTEROID_SPAWN_MIN_Y,
                max(PVP_ASTEROID_SPAWN_MIN_Y, max_y),
            )
            candidate = pygame.Rect(int(x_value), int(y_value), asteroid.width, asteroid.height)
            safe = True
            for player in self.players.values():
                expanded = player.ship.hitbox.inflate(
                    PVP_ASTEROID_PLAYER_SAFE_DISTANCE * 2,
                    PVP_ASTEROID_PLAYER_SAFE_DISTANCE * 2,
                )
                if candidate.colliderect(expanded):
                    safe = False
                    break
            if safe:
                asteroid.x = candidate.x
                asteroid.y = candidate.y
                asteroid.update()
                asteroid.y = candidate.y
                self.asteroids[uuid.uuid4().hex[:10]] = asteroid
                return

    def _add_effect(self, x: float, y: float, scale: float = 0.8) -> None:
        effect_id = uuid.uuid4().hex[:10]
        self.effects[effect_id] = DuelEffect(
            effect_id=effect_id,
            x=float(x),
            y=float(y),
            scale=float(scale),
            created_at=time.monotonic(),
            image=self.assets.get("explosion_img"),
        )

    def _fire_weapon_host(self, player_id: str, weapon: str) -> None:
        duel_player = self.players.get(str(player_id))
        if duel_player is None or duel_player.eliminated or duel_player.ship is None:
            return
        if not duel_player.ship or not getattr(duel_player.ship, "lives", 0):
            return

        if weapon == "laser":
            shots = duel_player.ship.shoot()
            for shot in shots or []:
                shot.direction = -1 if duel_player.role == "bottom" else 1
                shot.owner_id = duel_player.player_id
                self.projectiles.append(
                    DuelProjectile(
                        projectile_id=uuid.uuid4().hex[:10],
                        owner_id=duel_player.player_id,
                        weapon="laser",
                        obj=shot,
                        damage=WEAPON_DAMAGE["laser"],
                    )
                )
            duel_player.stats.shots_fired += len(shots or [])
            return

        if weapon == "torpedo":
            torpedo = duel_player.ship.torpedo()
            if torpedo is None:
                return
            torpedo.direction = -1 if duel_player.role == "bottom" else 1
            torpedo.owner_id = duel_player.player_id
            self.projectiles.append(
                DuelProjectile(
                    projectile_id=uuid.uuid4().hex[:10],
                    owner_id=duel_player.player_id,
                    weapon="torpedo",
                    obj=torpedo,
                    damage=WEAPON_DAMAGE["torpedo"],
                )
            )
            duel_player.stats.shots_fired += 1

    def _apply_player_damage(self, attacker_id: Optional[str], victim: DuelPlayer, damage: int) -> None:
        if victim.eliminated or not victim.ship.lives or victim.ship.is_invulnerable():
            return
        attacker = self.players.get(attacker_id) if attacker_id else None
        died = victim.ship.take_damage(damage)
        self._add_effect(victim.ship.hitbox.centerx, victim.ship.hitbox.centery, 0.9)

        if attacker is not None:
            attacker.stats.hits += 1
            attacker.stats.damage_dealt += damage
            attacker_score = PVP_HIT_SCORE
            self._add_score(attacker, attacker_score)

        now = time.monotonic()
        if died:
            victim.stats.survival_time_ms += int(max(0.0, now - victim.alive_since) * 1000)
            victim.eliminated = True
            victim.respawn_at = 0.0
            if attacker is not None:
                attacker.stats.kills += 1
                self._add_score(attacker, PVP_KILL_SCORE)
            victim.ship.lives = 0
            victim.ship.invulnerable_until = 0
        else:
            victim.stats.survival_time_ms += int(max(0.0, now - victim.alive_since) * 1000)
            victim.respawn_at = now + PVP_RESPAWN_DELAY_MS / 1000.0
            victim.alive_since = 0.0
            # The ship is hidden during the respawn delay and becomes immune
            # for the configured period immediately after it reappears.
            victim.ship.invulnerable_until = pygame.time.get_ticks() + PVP_RESPAWN_DELAY_MS

    def _add_score(self, player: DuelPlayer, amount: int) -> None:
        # PvP score is kept externally from Player because the original Player
        # class intentionally contains only movement/lives responsibilities.
        player.score = max(0, int(player.score) + int(amount))

    def _handle_respawns(self, now: float) -> None:
        for player in self.players.values():
            if player.eliminated or player.respawn_at <= 0.0:
                continue
            if now < player.respawn_at:
                continue
            player.reset_spawn(
                self.source_width,
                self.source_height,
                now,
                invulnerable_ms=PVP_RESPAWN_INVULNERABILITY_MS,
            )

    def _move_player(self, duel_player: DuelPlayer, left: bool, right: bool) -> None:
        if duel_player.eliminated or duel_player.respawn_at > 0.0:
            return
        if not duel_player.ship.lives:
            return
        if left and not right:
            duel_player.ship.move_left()
        elif right and not left:
            duel_player.ship.move_right(self.source_width)

    def _process_host_inputs(self, local_left: bool, local_right: bool) -> None:
        if self.session.server is None:
            return
        inputs, fire_events = self.session.server.consume_pvp_inputs()
        # Remote movement comes from the network server.
        for player_id, duel_player in self.players.items():
            if player_id == self.local_id:
                duel_player.last_input_left = bool(local_left)
                duel_player.last_input_right = bool(local_right)
            else:
                state = inputs.get(player_id, {})
                duel_player.last_input_left = bool(state.get("left", False))
                duel_player.last_input_right = bool(state.get("right", False))
            self._move_player(
                duel_player,
                duel_player.last_input_left,
                duel_player.last_input_right,
            )

        for fire in fire_events:
            self._fire_weapon_host(
                str(fire.get("player_id") or ""),
                str(fire.get("weapon") or "laser"),
            )

    def _update_host_projectiles(self) -> None:
        for projectile in self.projectiles[:]:
            projectile.obj.update()
            rect = projectile.obj.rect
            if rect.bottom < 0 or rect.top > self.source_height:
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
                continue

        if len(self.projectiles) > PVP_MAX_PROJECTILES:
            self.projectiles = self.projectiles[-PVP_MAX_PROJECTILES:]

    def _update_host_asteroids(self) -> None:
        if self.background is None:
            return
        difficulty = self.background.get_current_difficulty()
        profile = DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY]
        system_bonus = float(difficulty.get("system_bonus", 0.0))
        density = profile["asteroid_density"] * (1.0 + system_bonus * 0.80)
        interval = max(
            PVP_ASTEROID_MIN_SPAWN_INTERVAL,
            int(PVP_ASTEROID_BASE_SPAWN_INTERVAL / max(0.35, density)),
        )
        interval = max(PVP_ASTEROID_MIN_SPAWN_INTERVAL, interval)
        self._asteroid_spawn_timer += 1
        if self._asteroid_spawn_timer >= interval:
            self._spawn_safe_asteroid()
            self._asteroid_spawn_timer = 0

        for asteroid_id, asteroid in list(self.asteroids.items()):
            asteroid.update()
            if asteroid.y > self.source_height:
                self.asteroids.pop(asteroid_id, None)

    def _handle_host_collisions(self) -> None:
        # Projectiles hit asteroids first. This mirrors the existing game's
        # projectile-vs-asteroid priority before player collisions.
        for projectile in self.projectiles[:]:
            hit = False
            for asteroid_id, asteroid in list(self.asteroids.items()):
                if asteroid.get_rect().colliderect(projectile.obj.rect):
                    owner = self.players.get(projectile.owner_id)
                    if owner is not None:
                        self._add_score(owner, asteroid.get_points())
                    self._add_effect(
                        asteroid.x + asteroid.width / 2,
                        asteroid.y + asteroid.height / 2,
                        max(0.3, asteroid.scale),
                    )
                    self.asteroids.pop(asteroid_id, None)
                    hit = True
                    break
            if hit:
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
                continue

            # Only the opponent can be damaged.
            for player_id, victim in self.players.items():
                if player_id == projectile.owner_id or victim.eliminated or victim.respawn_at > 0.0:
                    continue
                if victim.ship.is_invulnerable():
                    continue
                if victim.ship.hitbox.colliderect(projectile.obj.rect):
                    self._apply_player_damage(projectile.owner_id, victim, projectile.damage)
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    break

        # Asteroids can damage both players. They are removed after impact,
        # exactly like the original single-player collision.
        for asteroid_id, asteroid in list(self.asteroids.items()):
            asteroid_rect = asteroid.get_rect()
            impacted = False
            for player in self.players.values():
                if player.eliminated or player.respawn_at > 0.0 or player.ship.is_invulnerable():
                    continue
                if asteroid_rect.colliderect(player.ship.hitbox):
                    self._apply_player_damage(None, player, 1)
                    self.asteroids.pop(asteroid_id, None)
                    self._add_effect(
                        asteroid.x + asteroid.width / 2,
                        asteroid.y + asteroid.height / 2,
                        max(0.3, asteroid.scale),
                    )
                    impacted = True
                    break
            if impacted:
                continue

    def _update_host_system_transition(self, global_score: int) -> None:
        if self.background is None:
            return
        self.background.update(global_score)

        tm = self.background.transition_manager
        active = tm.is_active()
        signature = None
        if active:
            target_id = getattr(getattr(tm, "transition_to", None), "id_name", "")
            signature = (
                int(tm.target_order_index),
                target_id,
            )
        if signature != self._last_transition_signature:
            if signature is not None:
                self.asteroids.clear()
                self.projectiles.clear()
                self._asteroid_spawn_timer = 0
            self._last_transition_signature = signature

    def _host_result(self) -> Optional[dict]:
        alive = [player for player in self.players.values() if not player.eliminated]
        if self.mode == "last_survivor":
            eliminated = [player for player in self.players.values() if player.eliminated]
            if len(eliminated) >= 1 and len(alive) <= 1:
                if len(alive) == 1:
                    winner = alive[0]
                    return self._make_result(winner.player_id)
                return self._make_result(None)
            return None

        # Timed score fight.
        if self.match_elapsed_ms >= PVP_SCORE_LIMIT_MS:
            rows = sorted(
                self.players.values(),
                key=lambda player: int(getattr(player, "score", 0)),
                reverse=True,
            )
            if len(rows) >= 2 and int(getattr(rows[0], "score", 0)) == int(getattr(rows[1], "score", 0)):
                return self._make_result(None)
            return self._make_result(rows[0].player_id if rows else None)
        return None

    def _make_result(self, winner_id: Optional[str]) -> dict:
        return {
            "winner_id": winner_id,
            "mode": self.mode,
            "players": [self._player_snapshot(player) for player in self.players.values()],
        }

    def _player_snapshot(self, player: DuelPlayer) -> dict:
        now = time.monotonic()
        survival_ms = player.stats.survival_time_ms
        if not player.eliminated and player.alive_since > 0.0:
            survival_ms += int(max(0.0, now - player.alive_since) * 1000)
        return {
            "id": player.player_id,
            "name": player.name,
            "ship": player.ship_name,
            "role": player.role,
            "x": float(player.ship.x),
            "y": float(player.ship.y),
            "width": int(player.ship.width),
            "height": int(player.ship.height),
            "score": int(getattr(player, "score", 0)),
            "lives": int(player.ship.lives),
            "alive": bool(not player.eliminated and player.respawn_at <= 0.0 and player.ship.lives > 0),
            "eliminated": bool(player.eliminated),
            "kills": int(player.stats.kills),
            "hits": int(player.stats.hits),
            "shots": int(player.stats.shots_fired),
            "damage": int(player.stats.damage_dealt),
            "survival_ms": max(0, int(survival_ms)),
            "invulnerable": bool(player.ship.is_invulnerable()),
        }

    def _transition_snapshot(self) -> dict:
        if self.background is None:
            return {"active": False}
        tm = self.background.transition_manager
        if not tm.is_active():
            return {"active": False}
        elapsed = pygame.time.get_ticks() - tm.transition_start
        return {
            "active": True,
            "target_index": int(tm.target_order_index),
            "from_index": int(self.background.systems.order_index),
            "elapsed_ms": max(0, int(elapsed)),
            "duration_ms": int(tm.phase_durations[0] if tm.phase_durations else 5000),
        }

    def _host_snapshot(self) -> dict:
        asteroids = []
        for asteroid_id, asteroid in self.asteroids.items():
            asteroids.append({
                "id": asteroid_id,
                "x": float(asteroid.x),
                "y": float(asteroid.y),
                "width": int(asteroid.width),
                "height": int(asteroid.height),
                "scale": float(asteroid.scale),
                "frame": int(asteroid.frame),
            })

        projectiles = []
        for projectile in self.projectiles:
            rect = projectile.obj.rect
            projectiles.append({
                "id": projectile.projectile_id,
                "owner_id": projectile.owner_id,
                "weapon": projectile.weapon,
                "x": float(rect.x),
                "y": float(rect.y),
                "width": int(rect.width),
                "height": int(rect.height),
            })

        now = time.monotonic()
        active_effects = []
        for effect_id, effect in list(self.effects.items()):
            age_ms = int((now - effect.created_at) * 1000)
            if age_ms > PVP_EXPLOSION_DURATION_MS:
                self.effects.pop(effect_id, None)
                continue
            active_effects.append({
                "id": effect_id,
                "x": effect.x,
                "y": effect.y,
                "scale": effect.scale,
                "age_ms": age_ms,
            })

        global_score = sum(int(getattr(player, "score", 0)) for player in self.players.values())
        return {
            "type": "pvp_snapshot",
            "version": 1,
            "mode": self.mode,
            "source_width": self.source_width,
            "source_height": self.source_height,
            "match_elapsed_ms": int(self.match_elapsed_ms),
            "match_time_limit_ms": PVP_SCORE_LIMIT_MS,
            "system_index": int(self.background.systems.order_index) if self.background else 0,
            "system_name": self.background.get_current_system_name() if self.background else "",
            "system_order": list(self._last_system_order),
            "transition": self._transition_snapshot(),
            "players": [self._player_snapshot(player) for player in self.players.values()],
            "asteroids": asteroids,
            "projectiles": projectiles,
            "effects": active_effects,
            "match_over": bool(self.match_over),
            "result": self.result,
            "global_score": global_score,
        }

    def _send_host_snapshot(self, force: bool = False) -> None:
        if self.session.server is None:
            return
        now = time.monotonic()
        if not force and (now - self._last_snapshot_sent) * 1000 < PVP_SNAPSHOT_INTERVAL_MS:
            return
        self._last_snapshot_sent = now
        self.session.server.broadcast_pvp_snapshot(self._host_snapshot())

    def update_host(self, local_left: bool, local_right: bool, dt: float, width: int, height: int, fire_events: List[str]) -> None:
        if self.background is None:
            self.source_width = width
            self.source_height = height
        self._setup_host_world(width, height)
        if not self.players:
            return

        # If the host window changes, resize local world and respawn positions.
        if width != self.source_width or height != self.source_height:
            self.source_width = width
            self.source_height = height
            if self.background:
                self.background.resize(width, height)
            for player in self.players.values():
                player.reset_spawn(width, height, time.monotonic(), invulnerable_ms=200)
            for asteroid in self.asteroids.values():
                asteroid.resize(width, height)

        now = time.monotonic()
        self.match_elapsed_ms = int((now - self.match_started_at) * 1000)

        # A disconnected opponent is treated as eliminated. The remaining
        # player can therefore win without waiting for another network packet.
        connected_ids = {str(player_id) for player_id in self.session.players.keys()}
        disconnected_opponent = False
        for player_id, duel_player in self.players.items():
            if player_id not in connected_ids and player_id != str(self.local_id):
                if not duel_player.eliminated:
                    duel_player.eliminated = True
                    duel_player.respawn_at = 0.0
                    duel_player.ship.lives = 0
                    disconnected_opponent = True
        self._handle_respawns(now)
        if disconnected_opponent and not self.match_over:
            remaining = [player for player in self.players.values() if not player.eliminated]
            self.match_over = True
            self.result = self._make_result(remaining[0].player_id if len(remaining) == 1 else None)
            self._result_started_at = time.monotonic()

        self._process_host_inputs(local_left, local_right)
        for weapon in fire_events:
            self._fire_weapon_host(self.local_id, weapon)

        self._update_host_projectiles()
        self._update_host_asteroids()
        self._handle_host_collisions()

        total_score = sum(int(getattr(player, "score", 0)) for player in self.players.values())
        self._update_host_system_transition(total_score)

        result = self._host_result()
        if result is not None and not self.match_over:
            self.match_over = True
            self.result = result
            self._result_started_at = time.monotonic()

        self._send_host_snapshot()

    # ------------------------------------------------------------------
    # Client side: input, snapshot interpolation and rendering
    # ------------------------------------------------------------------
    def _send_client_input(self, left: bool, right: bool) -> None:
        now = time.monotonic()
        if now - self._last_input_sent < PVP_INPUT_INTERVAL_MS / 1000.0:
            return
        self._last_input_sent = now
        self.session.client.send_pvp_input(left, right)

    def handle_local_event(self, event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self._quit_requested = True
            return
        if self.is_host:
            return
        if self.match_over:
            return
        if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
            self._fire_sequence += 1
            self.session.client.send_pvp_fire("laser", self._fire_sequence)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self._fire_sequence += 1
            self.session.client.send_pvp_fire("torpedo", self._fire_sequence)

    def handle_host_local_event(self, event, fire_events: List[str]) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                fire_events.append("laser")
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                fire_events.append("torpedo")
            elif event.key == pygame.K_ESCAPE:
                self._quit_requested = True

    def _apply_snapshot(self, snapshot: dict, width: int, height: int) -> None:
        self.latest_snapshot = snapshot
        self.source_width = max(320, int(snapshot.get("source_width", width) or width))
        self.source_height = max(240, int(snapshot.get("source_height", height) or height))

        system_order = snapshot.get("system_order") or []
        if self.background is None:
            self.background = BackgroundManager(width, height, self.assets, auto_switch=False)
        if system_order and system_order != self._last_system_order:
            self._last_system_order = list(system_order)
            self.background.set_system_order_by_ids(self._last_system_order)

        target_system = int(snapshot.get("system_index", 0))
        transition = snapshot.get("transition") or {}
        if transition.get("active"):
            signature = (int(transition.get("target_index", 0)), int(transition.get("duration_ms", 0)))
            if signature != self._last_transition_signature:
                self._last_transition_signature = signature
                self.background.start_synchronized_transition(
                    signature[0],
                    int(transition.get("elapsed_ms", 0)),
                    signature[1] or 5000,
                )
        elif self.background.systems.order_index != target_system:
            self.background.sync_to_system_index(target_system)
            self._last_transition_signature = None

        raw_players = snapshot.get("players") or []
        seen = set()
        for data in raw_players:
            if not isinstance(data, dict):
                continue
            player_id = str(data.get("id") or "")
            if not player_id:
                continue
            seen.add(player_id)
            world_x = float(data.get("x", 0.0) or 0.0)
            world_y = float(data.get("y", 0.0) or 0.0)
            view = self.view_players.get(player_id)
            if view is None:
                view = DuelViewPlayer(
                    player_id=player_id,
                    name=str(data.get("name") or "Spieler")[:20],
                    ship=str(data.get("ship") or "xwing"),
                    role=str(data.get("role") or "bottom"),
                    x=world_x,
                    y=world_y,
                    width=int(data.get("width", 80) or 80),
                    height=int(data.get("height", 80) or 80),
                    score=0,
                    lives=3,
                    alive=True,
                    eliminated=False,
                    kills=0,
                    hits=0,
                    shots=0,
                    damage=0,
                    survival_ms=0,
                )
                self.view_players[player_id] = view
            view.name = str(data.get("name") or view.name)[:20]
            view.ship = str(data.get("ship") or view.ship)
            view.role = str(data.get("role") or view.role)
            view.width = int(data.get("width", view.width) or view.width)
            view.height = int(data.get("height", view.height) or view.height)
            view.score = max(0, int(data.get("score", view.score) or 0))
            view.lives = max(0, int(data.get("lives", view.lives) or 0))
            view.alive = bool(data.get("alive", view.alive))
            view.eliminated = bool(data.get("eliminated", view.eliminated))
            view.kills = max(0, int(data.get("kills", view.kills) or 0))
            view.hits = max(0, int(data.get("hits", view.hits) or 0))
            view.shots = max(0, int(data.get("shots", view.shots) or 0))
            view.damage = max(0, int(data.get("damage", view.damage) or 0))
            view.survival_ms = max(0, int(data.get("survival_ms", view.survival_ms) or 0))
            view.invulnerable = bool(data.get("invulnerable", False))
            view.set_target(world_x, world_y)
        for player_id in list(self.view_players):
            if player_id not in seen:
                self.view_players.pop(player_id, None)

        # Snapshot asteroids/projectiles are authoritative. Rendering only needs
        # their latest states; interpolation is applied to the ship positions.
        self._client_asteroids = list(snapshot.get("asteroids") or [])
        self._client_projectiles = list(snapshot.get("projectiles") or [])

        now = time.monotonic()
        for effect in snapshot.get("effects") or []:
            if not isinstance(effect, dict):
                continue
            effect_id = str(effect.get("id") or "")
            if not effect_id:
                continue
            if effect_id not in self.client_effects:
                self.client_effects[effect_id] = DuelEffect(
                    effect_id=effect_id,
                    x=float(effect.get("x", 0.0) or 0.0),
                    y=float(effect.get("y", 0.0) or 0.0),
                    scale=float(effect.get("scale", 0.8) or 0.8),
                    created_at=now - max(0, int(effect.get("age_ms", 0))) / 1000.0,
                    image=self.assets.get("explosion_img"),
                )

        for effect_id, effect in list(self.client_effects.items()):
            if (now - effect.created_at) * 1000 > PVP_EXPLOSION_DURATION_MS:
                self.client_effects.pop(effect_id, None)

        if snapshot.get("match_over"):
            self.match_over = True
            self.result = snapshot.get("result")
            if self._result_started_at <= 0.0:
                self._result_started_at = time.monotonic()

    def poll(self, width: int, height: int) -> None:
        events = self.session.poll(width, height)
        latest = None
        for event in events:
            if event.get("type") == "pvp_snapshot":
                latest = event
            elif event.get("type") == "server_stopped":
                self._quit_requested = True
                self.match_over = True
                self.result = {"host_stopped": True}
        if latest is not None and not self.is_host:
            self._apply_snapshot(latest, width, height)
        if not self.is_host and self.background is not None:
            self.background.update(0)
        elif self.is_host:
            # The host can receive its own snapshots over loopback, but its
            # authoritative objects remain the render source. Keep the latest
            # snapshot only for the result/scoreboard fallback.
            self.latest_snapshot = latest

    def update_client(self, width: int, height: int, left: bool, right: bool) -> None:
        self._send_client_input(left, right)
        self.poll(width, height)

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _world_to_view(x: float, y: float, obj_height: float, role_local: str, source_height: float, view_height: float):
        scale_y = view_height / max(1.0, source_height)
        y_scaled = y * scale_y
        h_scaled = obj_height * scale_y
        if role_local == "top":
            y_scaled = view_height - y_scaled - h_scaled
        return x, y_scaled

    def _local_role(self) -> str:
        if self.is_host and self.local_id in self.players:
            return self.players[self.local_id].role
        local = self.view_players.get(str(self.local_id))
        return local.role if local else "bottom"

    def _draw_ship_surface(self, screen, image, x, y, width, height, role, local_role, alpha=255):
        sx = screen.get_width() / max(1, self.source_width)
        sy = screen.get_height() / max(1, self.source_height)
        scale = min(sx, sy)
        target_w = max(2, int(width * scale))
        target_h = max(2, int(height * scale))
        ship_image = pygame.transform.smoothscale(image, (target_w, target_h))
        if role != local_role:
            ship_image = pygame.transform.flip(ship_image, False, True)
        if alpha < 255:
            ship_image = ship_image.convert_alpha()
            ship_image.set_alpha(alpha)
        view_x = x * sx
        view_y = y * sy
        if local_role == "top":
            view_y = screen.get_height() - view_y - ship_image.get_height()
        rect = ship_image.get_rect(topleft=(int(view_x), int(view_y)))
        glow = pygame.Surface((rect.width + 18, rect.height + 18), pygame.SRCALPHA)
        pygame.draw.rect(glow, (120, 220, 255, 32), glow.get_rect(), width=3, border_radius=8)
        screen.blit(glow, (rect.x - 9, rect.y - 9))
        screen.blit(ship_image, rect)
        return rect

    def _draw_label(self, screen, rect, text, alpha=220):
        font = pygame.font.Font(None, max(20, int(screen.get_height() * 0.030)))
        label = font.render(text, True, (235, 245, 255))
        label.set_alpha(alpha)
        label_rect = label.get_rect(center=(rect.centerx, rect.top - 10))
        screen.blit(label, label_rect)

    def _draw_host_world(self, screen):
        if self.background is not None:
            self.background.draw(screen)
        local_role = self._local_role()
        # Draw asteroids first.
        sx = screen.get_width() / max(1, self.source_width)
        sy = screen.get_height() / max(1, self.source_height)
        images = self.assets.get("asteroid_images", [])
        for asteroid in self.asteroids.values():
            image = images[asteroid.frame % len(images)] if images else asteroid.image
            target = pygame.transform.smoothscale(
                image,
                (max(2, int(asteroid.width * sx)), max(2, int(asteroid.height * sy))),
            )
            ax = asteroid.x * sx
            ay = asteroid.y * sy
            if local_role == "top":
                ay = screen.get_height() - ay - target.get_height()
            screen.blit(target, (int(ax), int(ay)))

        # Projectiles are world-authoritative and perspective-flipped together
        # with the world, so each player sees their own shots fly upward.
        for projectile in self.projectiles:
            rect = projectile.obj.rect
            px = rect.x * sx
            py = rect.y * sy
            pw = max(2, int(rect.width * sx))
            ph = max(2, int(rect.height * sy))
            if local_role == "top":
                py = screen.get_height() - py - ph
            if projectile.weapon == "torpedo" and getattr(projectile.obj, "image", None) is not None:
                image = pygame.transform.smoothscale(projectile.obj.image, (pw, ph))
                if local_role == "top":
                    image = pygame.transform.flip(image, False, True)
                screen.blit(image, (int(px), int(py)))
            else:
                pygame.draw.rect(screen, (255, 70, 70), pygame.Rect(int(px), int(py), pw, ph))

        # Ships after obstacles/projectiles.
        for player in self.players.values():
            image = self.assets.get(SHIP_ASSET_KEYS.get(player.ship_name))
            if image is None:
                continue
            alive = not player.eliminated and player.respawn_at <= 0.0 and player.ship.lives > 0
            if not alive:
                if player.eliminated:
                    label_player = f"{player.name} – GAME OVER"
                    dummy = pygame.Rect(int(player.ship.x), int(player.ship.y), player.ship.width, player.ship.height)
                    self._draw_label(screen, dummy, label_player, 150)
                continue
            alpha = 255 if player.player_id == self.local_id else 215
            if player.ship.is_invulnerable():
                alpha = 130 if player.player_id != self.local_id else 230
            rect = self._draw_ship_surface(
                screen,
                image,
                player.ship.x,
                player.ship.y,
                player.ship.width,
                player.ship.height,
                player.role,
                local_role,
                alpha=alpha,
            )
            self._draw_label(screen, rect, player.name)

        for effect in self.effects.values():
            self._draw_effect(screen, effect, local_role)

    def _draw_effect(self, screen, effect: DuelEffect, local_role: str):
        if effect.image is None:
            return
        age_ratio = min(1.0, max(0.0, (time.monotonic() - effect.created_at) * 1000 / PVP_EXPLOSION_DURATION_MS))
        scale = max(0.1, effect.scale * (0.65 + 0.45 * age_ratio))
        sx = screen.get_width() / max(1, self.source_width)
        sy = screen.get_height() / max(1, self.source_height)
        image = pygame.transform.smoothscale(
            effect.image,
            (max(2, int(effect.image.get_width() * scale * sx)), max(2, int(effect.image.get_height() * scale * sy))),
        )
        image.set_alpha(max(0, int(255 * (1.0 - age_ratio))))
        x = effect.x * sx
        y = effect.y * sy
        if local_role == "top":
            y = screen.get_height() - y
        rect = image.get_rect(center=(int(x), int(y)))
        if local_role == "top":
            image = pygame.transform.flip(image, False, True)
        screen.blit(image, rect)

    def _draw_client_world(self, screen):
        if self.background is not None:
            self.background.draw(screen)
        local_role = self._local_role()
        sx = screen.get_width() / max(1, self.source_width)
        sy = screen.get_height() / max(1, self.source_height)
        images = self.assets.get("asteroid_images", [])
        for asteroid in getattr(self, "_client_asteroids", []):
            if not isinstance(asteroid, dict) or not images:
                continue
            frame = int(asteroid.get("frame", 0)) % len(images)
            image = images[frame]
            width = max(2, int(float(asteroid.get("width", image.get_width())) * sx))
            height = max(2, int(float(asteroid.get("height", image.get_height())) * sy))
            image = pygame.transform.smoothscale(image, (width, height))
            x = float(asteroid.get("x", 0.0)) * sx
            y = float(asteroid.get("y", 0.0)) * sy
            if local_role == "top":
                y = screen.get_height() - y - height
            screen.blit(image, (int(x), int(y)))

        for projectile in getattr(self, "_client_projectiles", []):
            if not isinstance(projectile, dict):
                continue
            x = float(projectile.get("x", 0.0)) * sx
            y = float(projectile.get("y", 0.0)) * sy
            w = max(2, int(float(projectile.get("width", 6)) * sx))
            h = max(2, int(float(projectile.get("height", 20)) * sy))
            if local_role == "top":
                y = screen.get_height() - y - h
            if projectile.get("weapon") == "torpedo" and self.assets.get("torpedo_img") is not None:
                image = pygame.transform.smoothscale(self.assets["torpedo_img"], (w, h))
                if local_role == "top":
                    image = pygame.transform.flip(image, False, True)
                screen.blit(image, image.get_rect(center=(int(x + w / 2), int(y + h / 2))))
            else:
                pygame.draw.rect(screen, (255, 70, 70), pygame.Rect(int(x), int(y), w, h))

        for view in self.view_players.values():
            image = self.assets.get(SHIP_ASSET_KEYS.get(view.ship))
            if image is None:
                continue
            alive = view.alive and not view.eliminated
            if not alive:
                label_text = f"{view.name} – GAME OVER" if view.eliminated else f"{view.name} – RESPAWN"
                sx2 = screen.get_width() / max(1, self.source_width)
                sy2 = screen.get_height() / max(1, self.source_height)
                dummy = pygame.Rect(int(view.x * sx2), int(view.y * sy2), max(2, int(view.width * sx2)), max(2, int(view.height * sy2)))
                if local_role == "top":
                    dummy.y = screen.get_height() - dummy.y - dummy.height
                self._draw_label(screen, dummy, label_text, 150)
                continue
            alpha = 255 if view.player_id == self.local_id else 215
            if view.invulnerable:
                alpha = 230 if view.player_id == self.local_id else 135
            rect = self._draw_ship_surface(
                screen,
                image,
                view.x,
                view.y,
                view.width,
                view.height,
                view.role,
                local_role,
                alpha=alpha,
            )
            self._draw_label(screen, rect, view.name)

        for effect in self.client_effects.values():
            self._draw_effect(screen, effect, local_role)

    def draw_world(self, screen: pygame.Surface) -> None:
        if self.is_host:
            self._draw_host_world(screen)
        else:
            self._draw_client_world(screen)

        # BackgroundManager.draw() already renders and completes synchronized
        # system transitions. No extra transition pass is needed here.

    def draw_hud(self, screen: pygame.Surface) -> None:
        local_id = str(self.local_id or "")
        if self.is_host:
            player = self.players.get(local_id)
            if player is None:
                return
            score = int(getattr(player, "score", 0))
            lives = player.ship.lives
            mode_text = "LETZTER ÜBERLEBENDER" if self.mode == "last_survivor" else "PUNKTEKAMPF"
            timer_text = ""
            if self.mode == "points":
                remaining = max(0, PVP_SCORE_LIMIT_MS - self.match_elapsed_ms)
                timer_text = f"  Zeit {remaining // 60000:02d}:{(remaining % 60000) // 1000:02d}"
        else:
            view = self.view_players.get(local_id)
            if view is None:
                return
            score = view.score
            lives = view.lives
            mode_text = "LETZTER ÜBERLEBENDER" if self.mode == "last_survivor" else "PUNKTEKAMPF"
            elapsed = int((self.latest_snapshot or {}).get("match_elapsed_ms", 0))
            remaining = max(0, PVP_SCORE_LIMIT_MS - elapsed)
            timer_text = f"  Zeit {remaining // 60000:02d}:{(remaining % 60000) // 1000:02d}" if self.mode == "points" else ""
        font = pygame.font.Font(None, max(24, int(screen.get_height() * 0.034)))
        label = font.render(f"Punkte: {score}   Leben: {lives}   {mode_text}{timer_text}", True, (255, 255, 255))
        screen.blit(label, (10, 10))

    def scoreboard_rows(self) -> List[dict]:
        if self.is_host:
            rows = []
            for player in self.players.values():
                rows.append({
                    "id": player.player_id,
                    "name": player.name,
                    "score": int(getattr(player, "score", 0)),
                    "alive": not player.eliminated,
                    "kills": player.stats.kills,
                    "damage": player.stats.damage_dealt,
                    "accuracy": player.stats.accuracy,
                })
        else:
            rows = []
            for view in self.view_players.values():
                accuracy = (view.hits / view.shots * 100.0) if view.shots else 0.0
                rows.append({
                    "id": view.player_id,
                    "name": view.name,
                    "score": view.score,
                    "alive": view.alive,
                    "kills": view.kills,
                    "damage": view.damage,
                    "accuracy": accuracy,
                })
        rows.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
        return rows

    def draw_scoreboard(self, screen: pygame.Surface) -> None:
        rows = self.scoreboard_rows()
        width, height = screen.get_size()
        row_h = max(34, int(min(width, height) * 0.065))
        panel_w = min(width - 50, 700)
        panel_h = 92 + max(2, len(rows)) * row_h
        panel = pygame.Rect((width - panel_w) // 2, (height - panel_h) // 2, panel_w, panel_h)
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (14, 18, 34), panel, border_radius=18)
        pygame.draw.rect(screen, (110, 215, 255), panel, 2, border_radius=18)
        title_font = pygame.font.Font(None, max(30, int(height * 0.055)))
        text_font = pygame.font.Font(None, max(22, int(height * 0.032)))
        title = title_font.render("PVP-DUELL", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 30)))
        header_y = panel.y + 57
        columns = [panel.x + 25, panel.x + 70, panel.x + int(panel_w * 0.50), panel.x + int(panel_w * 0.69), panel.x + int(panel_w * 0.84)]
        for text, x in zip(("#", "Spieler", "Punkte", "KOs", "Treffer%"), columns):
            screen.blit(text_font.render(text, True, (160, 175, 200)), (x, header_y))
        for idx, row in enumerate(rows[:2], start=1):
            y = panel.y + 91 + (idx - 1) * row_h
            local = str(row.get("id")) == str(self.local_id)
            if local:
                hi = pygame.Surface((panel_w - 30, row_h - 4), pygame.SRCALPHA)
                hi.fill((0, 150, 255, 38))
                screen.blit(hi, (panel.x + 15, y - 3))
            accuracy = row.get("accuracy", 0.0)
            values = [
                str(idx),
                str(row.get("name") or "Spieler")[:18],
                f"{int(row.get('score', 0)):,}".replace(",", "."),
                str(int(row.get("kills", 0))),
                f"{float(accuracy):.1f}%",
            ]
            for value, x in zip(values, columns):
                color = (180, 235, 255) if local else (245, 245, 250)
                screen.blit(text_font.render(value, True, color), (x, y))

    # ------------------------------------------------------------------
    # Main loop / result screen
    # ------------------------------------------------------------------
    def run(self, screen, clock) -> dict:
        running = True
        fire_events: List[str] = []
        local_dead = False
        while running:
            dt = min(0.05, clock.tick(60) / 1000.0)
            width, height = screen.get_size()
            events = pygame.event.get()
            fire_events.clear()

            for event in events:
                if event.type == pygame.QUIT:
                    self.session.stop()
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.VIDEORESIZE:
                    width = max(480, event.w)
                    height = max(360, event.h)
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                    continue
                if self.is_host:
                    self.handle_host_local_event(event, fire_events)
                else:
                    self.handle_local_event(event)

            keys = pygame.key.get_pressed()
            left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

            if self.is_host:
                self.poll(width, height)
                self.update_host(bool(left), bool(right), dt, width, height, list(fire_events))
            else:
                self.update_client(width, height, bool(left), bool(right))

            if self._quit_requested:
                return {"quit": True}

            screen.fill((0, 0, 0))
            self.draw_world(screen)
            self.draw_hud(screen)

            # TAB keeps the game running and only adds an overlay.
            if keys[pygame.K_TAB] and not self.match_over:
                self.draw_scoreboard(screen)

            if self.match_over:
                self._draw_result_screen(screen)
                if time.monotonic() - self._result_started_at >= PVP_RESULT_DELAY_MS / 1000.0:
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                            return {"result": self.result}

            pygame.display.flip()

        return {"result": self.result}

    def _draw_result_screen(self, screen: pygame.Surface) -> None:
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))
        title_font = pygame.font.Font(None, max(48, int(height * 0.085)))
        text_font = pygame.font.Font(None, max(22, int(height * 0.035)))
        small_font = pygame.font.Font(None, max(20, int(height * 0.028)))

        if self.result and self.result.get("host_stopped"):
            title = title_font.render("HOST HAT DAS SPIEL BEENDET", True, (255, 180, 140))
            screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.25))))
            return

        winner_id = self.result.get("winner_id") if isinstance(self.result, dict) else None
        if winner_id:
            players = self.result.get("players", [])
            winner_name = next((p.get("name") for p in players if str(p.get("id")) == str(winner_id)), "Spieler")
            title_text = f"SIEGER: {winner_name}"
            color = (140, 255, 170)
        else:
            title_text = "UNENTSCHIEDEN"
            color = (255, 230, 140)
        title = title_font.render(title_text, True, color)
        screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.18))))
        subtitle = small_font.render(
            "Letzter Überlebender" if self.mode == "last_survivor" else "Punktekampf",
            True,
            (190, 200, 220),
        )
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.26))))

        players = list(self.result.get("players", [])) if isinstance(self.result, dict) else []
        start_y = int(height * 0.36)
        for idx, player in enumerate(players[:2]):
            panel = pygame.Rect(width // 2 - 330 + idx * 345, start_y, 315, 225)
            pygame.draw.rect(screen, (18, 22, 38), panel, border_radius=14)
            pygame.draw.rect(screen, (90, 105, 135), panel, 2, border_radius=14)
            name = text_font.render(str(player.get("name") or "Spieler"), True, (245, 245, 250))
            screen.blit(name, name.get_rect(center=(panel.centerx, panel.y + 28)))
            score = int(player.get("score", 0))
            hits = int(player.get("hits", 0))
            shots = int(player.get("shots", 0))
            accuracy = hits / shots * 100.0 if shots else 0.0
            survival = int(player.get("survival_ms", 0))
            if not player.get("eliminated"):
                # The host result snapshot already contains the final survival time.
                pass
            lines = [
                f"Punkte: {score}",
                f"Abschüsse: {int(player.get('kills', 0))}",
                f"Trefferquote: {accuracy:.1f}%",
                f"Überlebenszeit: {survival // 1000}s",
                f"Schaden: {int(player.get('damage', 0))}",
            ]
            for line_index, line in enumerate(lines):
                surf = small_font.render(line, True, (205, 215, 230))
                screen.blit(surf, (panel.x + 22, panel.y + 66 + line_index * 28))

        hint = small_font.render("ENTER / LEERTASTE / ESC = zurück zum Menü", True, (165, 175, 195))
        screen.blit(hint, hint.get_rect(center=(width // 2, height - 35)))
