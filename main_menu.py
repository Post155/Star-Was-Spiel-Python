"""Highly configurable cinematic start screen for a Star Wars inspired Pygame project.

This module intentionally stays fully self-contained and does not modify the existing
menu system. It is designed as a reusable entry screen that can later be replaced or
embedded into a larger game flow.

The screen focuses on production-ready presentation:
- layered cinematic space background
- animated title with glow and pulse
- configurable menu buttons with keyboard/controller focus support
- reusable procedural effects without external assets
- separation between logic and rendering
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional, Sequence, Tuple

import pygame


START_SCREEN_CONFIG: dict[str, Any] = {
    "TITLE": {
        "text": "STAR WARS",
        "subtitle": "THE GALACTIC FRONTIER",
        "font": "Impact",
        "size": 112,
        "subtitle_size": 28,
        "color": (234, 240, 255),
        "glow_color": (88, 164, 255),
        "pulse_speed": 2.6,
        "shadow_color": (13, 19, 30),
    },
    "BACKGROUND": {
        "star_count": 260,
        "star_speed": 1.4,
        "parallax_layers": [0.25, 0.55, 0.85],
        "nebula_enabled": True,
        "nebula_colors": [
            (36, 86, 146, 80),
            (132, 62, 179, 75),
            (74, 122, 212, 70),
            (194, 83, 65, 60),
        ],
        "particles_enabled": True,
        "asteroid_field_enabled": True,
    },
    "PLANETS": {
        "enabled": True,
        "count": 3,
        "size": (120, 170),
        "rotation_speed": 0.18,
        "spawn_locations": [
            (0.1, 0.22),
            (0.78, 0.18),
            (0.86, 0.55),
        ],
    },
    "FACTIONS": {
        "rebel_logo": "REBELLION",
        "empire_logo": "EMPIRE",
        "logo_size": 40,
        "logo_glow_color": (255, 92, 92),
        "logo_animation_speed": 1.3,
        "logo_offset": (0.24, 0.88),
        "empire_offset": (0.76, 0.89),
    },
    "SPACE_BATTLE": {
        "enable_xwings": True,
        "enable_tiefighters": True,
        "enable_star_destroyers": True,
        "enable_laser_fire": True,
        "ship_speed": 3.2,
        "ship_density": 0.8,
    },
    "BUTTONS": {
        "button_width": 290,
        "button_height": 62,
        "border_radius": 18,
        "idle_color": (22, 28, 37),
        "hover_color": (39, 52, 69),
        "hover_glow": (120, 175, 255),
        "hover_scale": 1.08,
        "animation_speed": 8.5,
        "text_color": (245, 248, 255),
        "text_hover_color": (255, 255, 255),
    },
    "AUDIO": {
        "music_enabled": False,
        "music_volume": 0.35,
        "hover_sound": "",
        "click_sound": "",
    },
    "EFFECTS": {
        "bloom_intensity": 20,
        "vignette_strength": 0.86,
        "screen_shake": 1.2,
        "particle_density": 0.6,
    },
    "LAYOUT": {
        "title_position": (0.5, 0.22),
        "subtitle_position": (0.5, 0.3),
        "menu_position": (0.5, 0.72),
        "faction_position": (0.5, 0.86),
    },
}


Vec2 = Tuple[float, float]


@dataclass
class StarParticle:
    """Single star in the deep-space backdrop."""

    x: float
    y: float
    radius: float
    speed: float
    alpha: float
    twinkle: float
    depth: float

    def update(self, width: int, height: int, speed_multiplier: float) -> None:
        self.y += self.speed * speed_multiplier * (0.6 + self.depth)
        if self.y > height + 6:
            self.y = -10
            self.x = random.random() * width
            self.radius = random.uniform(1.0, 3.2)
            self.speed = random.uniform(0.35, 2.0)
            self.alpha = random.uniform(0.3, 1.0)

    def draw(self, surface: pygame.Surface) -> None:
        alpha = int(max(0, min(255, self.alpha * 255)))
        color = (220, 230, 255, alpha)
        radius = max(1, self.radius)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)


@dataclass
class NebulaCloud:
    """Soft moving nebula cloud used as atmospheric background depth."""

    x: float
    y: float
    radius: float
    drift: float
    color: Tuple[int, int, int, int]
    phase: float

    def update(self, width: int, height: int, elapsed: float) -> None:
        self.x += self.drift * 0.35
        self.y += math.sin(elapsed * 0.5 + self.phase) * 0.12
        if self.x > width + self.radius:
            self.x = -self.radius
        if self.x < -self.radius:
            self.x = width + self.radius

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


@dataclass
class Asteroid:
    """Rocky debris in the outer space field."""

    x: float
    y: float
    radius: float
    speed: float
    angle: float
    spin: float
    color: Tuple[int, int, int]

    def update(self, width: int, height: int) -> None:
        self.y += self.speed
        self.x += math.sin(self.angle) * 0.8
        self.angle += self.spin
        if self.y > height + 60:
            self.x = random.random() * width
            self.y = -50
            self.radius = random.uniform(5, 18)
            self.speed = random.uniform(0.4, 2.2)

    def draw(self, surface: pygame.Surface) -> None:
        points = []
        for i in range(7):
            rad = self.angle + (i / 7.0) * math.tau
            dist = self.radius * (0.8 + 0.35 * math.sin(i * 2.1 + self.angle))
            points.append((int(self.x + math.cos(rad) * dist), int(self.y + math.sin(rad) * dist)))
        pygame.draw.polygon(surface, self.color, points, 1)


@dataclass
class Planet:
    """Large gaseous planet used as cinematic framing element."""

    x: float
    y: float
    radius: float
    color: Tuple[int, int, int]
    glow: Tuple[int, int, int]
    orbit_speed: float
    phase: float

    def draw(self, surface: pygame.Surface, elapsed: float) -> None:
        draw_x = int(self.x + math.sin(elapsed * self.orbit_speed + self.phase) * 14)
        draw_y = int(self.y + math.cos(elapsed * self.orbit_speed * 0.7 + self.phase) * 12)
        pygame.draw.circle(surface, self.glow, (draw_x, draw_y), int(self.radius * 1.45), 0)
        pygame.draw.circle(surface, self.color, (draw_x, draw_y), int(self.radius), 0)
        pygame.draw.circle(surface, (255, 255, 255, 80), (draw_x - 12, draw_y - 12), int(self.radius * 0.28), 0)


@dataclass
class SpaceShip:
    """Abstract capital ship or fighter moving across the background."""

    x: float
    y: float
    size: float
    speed: float
    direction: float
    kind: str
    tint: Tuple[int, int, int]
    laser_color: Tuple[int, int, int]
    drift: float

    def update(self, width: int, height: int, elapsed: float) -> None:
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed * 0.6 + math.sin(elapsed * 0.8 + self.drift) * 0.4
        if self.x < -120 or self.x > width + 120 or self.y < -120 or self.y > height + 120:
            self.reset(width, height)

    def reset(self, width: int, height: int) -> None:
        margin = 120
        if random.random() < 0.5:
            self.x = random.uniform(-margin, width + margin)
            self.y = -random.uniform(30, 180)
        else:
            self.x = width + random.uniform(30, 180)
            self.y = random.uniform(-margin, height + margin)
        self.direction = random.uniform(-math.pi * 0.75, math.pi * 0.75)
        self.speed = random.uniform(0.7, 2.8)

    def draw(self, surface: pygame.Surface, elapsed: float) -> None:
        # Draw a stylized spaceship silhouette. This allows the background to feel like a
        # live battle without depending on external art assets.
        center = (int(self.x), int(self.y))
        length = int(self.size * 6)
        wing = int(self.size * 2.2)
        angle = math.atan2(math.sin(self.direction), math.cos(self.direction))

        if self.kind == "xwing":
            points = [
                (center[0] + math.cos(angle) * length, center[1] + math.sin(angle) * length),
                (center[0] + math.cos(angle + math.pi / 4) * wing, center[1] + math.sin(angle + math.pi / 4) * wing),
                (center[0] + math.cos(angle - math.pi / 2) * wing * 0.7, center[1] + math.sin(angle - math.pi / 2) * wing * 0.7),
                (center[0] + math.cos(angle + math.pi / 2) * wing * 0.7, center[1] + math.sin(angle + math.pi / 2) * wing * 0.7),
                (center[0] + math.cos(angle - math.pi / 4) * wing, center[1] + math.sin(angle - math.pi / 4) * wing),
            ]
            color = self.tint
            pygame.draw.polygon(surface, color, points)
            pygame.draw.circle(surface, (255, 255, 255), center, max(2, int(self.size * 0.5)))
        elif self.kind == "tiefighter":
            points = [
                (center[0] + math.cos(angle) * length, center[1] + math.sin(angle) * length),
                (center[0] + math.cos(angle + math.pi * 0.72) * wing, center[1] + math.sin(angle + math.pi * 0.72) * wing),
                (center[0] + math.cos(angle + math.pi) * length * 0.35, center[1] + math.sin(angle + math.pi) * length * 0.35),
                (center[0] + math.cos(angle - math.pi * 0.72) * wing, center[1] + math.sin(angle - math.pi * 0.72) * wing),
            ]
            pygame.draw.polygon(surface, self.tint, points)
            pygame.draw.circle(surface, (255, 255, 255), center, max(2, int(self.size * 0.5)))
        else:
            body = pygame.Rect(center[0] - int(self.size * 3.2), center[1] - int(self.size * 0.75), int(self.size * 6.4), int(self.size * 1.5))
            pygame.draw.rect(surface, self.tint, body, border_radius=9)
            pygame.draw.rect(surface, (255, 255, 255), body.inflate(-8, -8), border_radius=7, width=2)

        if random.random() < 0.18:
            laser_end = (
                int(center[0] - math.cos(angle) * (length * 1.6)),
                int(center[1] - math.sin(angle) * (length * 1.6)),
            )
            pygame.draw.line(surface, self.laser_color, center, laser_end, 2)


@dataclass
class MenuButton:
    """Configurable interactive menu item with hover and selection states."""

    label: str
    index: int
    text_color: Tuple[int, int, int]
    width: int
    height: int
    radius: int
    base_color: Tuple[int, int, int]
    hover_color: Tuple[int, int, int]
    hover_glow: Tuple[int, int, int]
    font: pygame.font.Font
    selected: bool = False
    hovered: bool = False
    rect: pygame.Rect = field(default_factory=pygame.Rect)
    target_scale: float = 1.0
    current_scale: float = 1.0
    pulse: float = 0.0

    def update(self, dt: float) -> None:
        target = 1.08 if self.hovered or self.selected else 1.0
        self.target_scale = target
        self.current_scale += (self.target_scale - self.current_scale) * min(1.0, dt * 12.0)
        self.pulse += dt * 6.0

    def draw(self, surface: pygame.Surface, center_x: int, center_y: int, global_alpha: float = 1.0) -> None:
        content_width = self.width * self.current_scale
        content_height = self.height * self.current_scale
        rect = pygame.Rect(
            int(center_x - content_width / 2),
            int(center_y - content_height / 2),
            int(content_width),
            int(content_height),
        )
        self.rect = rect

        fill_color = self.hover_color if self.hovered or self.selected else self.base_color
        border_color = self.hover_glow if self.hovered or self.selected else (150, 160, 180)
        border_width = 2 if self.hovered or self.selected else 1

        if self.hovered or self.selected:
            glow = pygame.Surface((rect.width + 24, rect.height + 24), pygame.SRCALPHA)
            pygame.draw.rect(
                glow,
                (*self.hover_glow, int(70 * global_alpha)),
                glow.get_rect(),
                border_radius=self.radius + 10,
            )
            glow_rect = glow.get_rect(center=rect.center)
            surface.blit(glow, glow_rect)

        pygame.draw.rect(
            surface,
            (*fill_color, int(255 * global_alpha)),
            rect,
            border_radius=self.radius,
            border_top_left_radius=self.radius,
            border_bottom_left_radius=self.radius,
            border_top_right_radius=self.radius,
            border_bottom_right_radius=self.radius,
        )
        pygame.draw.rect(
            surface,
            (*border_color, int(200 * global_alpha)),
            rect,
            border_radius=self.radius,
            width=border_width,
        )

        text = self.font.render(self.label, True, self.text_color)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)


class StartingScreen:
    """Cinematic starting screen with layered space atmosphere and interactive menu.

    The class intentionally exposes a simple public API so it can be swapped into a larger
    game loop without changing the surrounding architecture.
    """

    def __init__(self, screen: Optional[pygame.Surface] = None) -> None:
        self.config = START_SCREEN_CONFIG
        if screen is None:
            screen = pygame.display.get_surface()
        self.screen = screen if screen is not None else pygame.Surface((1280, 720))
        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_index = 0
        self.menu_items = ["Singleplayer", "Multiplayer", "Settings", "Quit"]
        self.last_time = time.monotonic()
        self.elapsed = 0.0
        self.ui_alpha = 255
        self.screen_shake = 0.0
        self._navigation_lock = 0.0

        self.fonts: dict[str, pygame.font.Font] = {}
        self._load_fonts()
        self.background = self._build_background()
        self.planets = self._build_planets()
        self.menu_buttons = self._build_buttons()
        self.rebel_logo = self._make_faction_label("REBELLION")
        self.empire_logo = self._make_faction_label("EMPIRE")
        self._play_hover_sound = False

    def _load_fonts(self) -> None:
        self.fonts["title"] = pygame.font.SysFont(self.config["TITLE"]["font"], self.config["TITLE"]["size"])
        self.fonts["subtitle"] = pygame.font.SysFont(self.config["TITLE"]["font"], self.config["TITLE"]["subtitle_size"])
        self.fonts["button"] = pygame.font.SysFont("Arial", 24, bold=True)
        self.fonts["faction"] = pygame.font.SysFont("Arial", self.config["FACTIONS"]["logo_size"], bold=True)

    def _build_background(self) -> dict[str, Any]:
        width, height = self.width, self.height
        stars = [
            StarParticle(
                x=random.random() * width,
                y=random.random() * height,
                radius=random.uniform(1.0, 3.2),
                speed=random.uniform(0.5, 2.0),
                alpha=random.uniform(0.2, 1.0),
                twinkle=random.random() * math.tau,
                depth=random.uniform(0.5, 1.8),
            )
            for _ in range(self.config["BACKGROUND"]["star_count"])
        ]
        nebula = [
            NebulaCloud(
                x=random.random() * width,
                y=random.random() * height,
                radius=random.uniform(140, 340),
                drift=random.uniform(-0.4, 0.7),
                color=(*random.choice(self.config["BACKGROUND"]["nebula_colors"])[:3], random.choice([60, 80, 100, 120])),
                phase=random.random() * math.tau,
            )
            for _ in range(6)
        ]
        asteroids = [
            Asteroid(
                x=random.random() * width,
                y=random.random() * height,
                radius=random.uniform(6, 18),
                speed=random.uniform(0.5, 2.2),
                angle=random.random() * math.tau,
                spin=random.uniform(-0.08, 0.08),
                color=(150, 160, 170),
            )
            for _ in range(26)
        ]

        battle_ships = []
        ship_cfg = self.config["SPACE_BATTLE"]
        for _ in range(int(5 + ship_cfg["ship_density"] * 10)):
            kind = "xwing" if ship_cfg["enable_xwings"] and random.random() < 0.5 else "tiefighter"
            if not ship_cfg["enable_tiefighters"] and kind == "tiefighter":
                kind = "xwing"
            if kind == "xwing":
                tint = (164, 194, 255)
                laser = (120, 180, 255)
            else:
                tint = (210, 90, 90)
                laser = (255, 100, 100)
            battle_ships.append(
                SpaceShip(
                    x=random.random() * width,
                    y=random.random() * height,
                    size=random.uniform(2.5, 4.0),
                    speed=random.uniform(0.8, 2.8) * ship_cfg["ship_speed"],
                    direction=random.random() * math.tau,
                    kind=kind,
                    tint=tint,
                    laser_color=laser,
                    drift=random.random() * math.tau,
                )
            )
        return {"stars": stars, "nebula": nebula, "asteroids": asteroids, "ships": battle_ships}

    def _build_planets(self) -> list[Planet]:
        planets: list[Planet] = []
        if not self.config["PLANETS"]["enabled"]:
            return planets
        width, height = self.width, self.height
        for index, location in enumerate(self.config["PLANETS"]["spawn_locations"]):
            x = location[0] * width
            y = location[1] * height
            palette = [
                ((50, 82, 125), (97, 163, 255)),
                ((120, 96, 58), (224, 181, 93)),
                ((76, 84, 118), (156, 140, 255)),
            ]
            color, glow = palette[index % len(palette)]
            planets.append(
                Planet(
                    x=x,
                    y=y,
                    radius=random.uniform(45, 100),
                    color=color,
                    glow=glow,
                    orbit_speed=random.uniform(0.08, 0.26),
                    phase=random.random() * math.tau,
                )
            )
        return planets

    def _build_buttons(self) -> list[MenuButton]:
        cfg = self.config["BUTTONS"]
        button_names = self.menu_items
        buttons: list[MenuButton] = []
        for i, label in enumerate(button_names):
            buttons.append(
                MenuButton(
                    label=label,
                    index=i,
                    text_color=cfg["text_color"],
                    width=cfg["button_width"],
                    height=cfg["button_height"],
                    radius=cfg["border_radius"],
                    base_color=cfg["idle_color"],
                    hover_color=cfg["hover_color"],
                    hover_glow=cfg["hover_glow"],
                    font=self.fonts["button"],
                    selected=i == self.selected_index,
                )
            )
        return buttons

    def _make_faction_label(self, text: str) -> pygame.Surface:
        font = self.fonts["faction"]
        glow = font.render(text, True, self.config["FACTIONS"]["logo_glow_color"])
        base = font.render(text, True, (235, 240, 250))
        shadow = font.render(text, True, (25, 32, 42))
        surface = pygame.Surface((shadow.get_width() + 60, shadow.get_height() + 50), pygame.SRCALPHA)
        surface.blit(shadow, (18, 18))
        surface.blit(glow, (0, 0))
        surface.blit(base, (10, 8))
        return surface

    def _update_button_hover(self) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            hovered = button.rect.collidepoint(mouse_x, mouse_y) if button.rect else False
            button.hovered = hovered
            if hovered:
                self.selected_index = button.index

    def _update_navigation(self, dt: float, key_input: Optional[Sequence[int]] = None) -> None:
        if key_input is None:
            key_input = []
        if self._navigation_lock > 0:
            self._navigation_lock -= dt

        if self._navigation_lock <= 0:
            if 273 in key_input or 119 in key_input:
                self.selected_index = (self.selected_index - 1) % len(self.menu_buttons)
                self._navigation_lock = 0.16
            if 274 in key_input or 115 in key_input:
                self.selected_index = (self.selected_index + 1) % len(self.menu_buttons)
                self._navigation_lock = 0.16
            if 13 in key_input or 32 in key_input:
                self._trigger_menu_action(self.selected_index)
                self._navigation_lock = 0.2

        for index, button in enumerate(self.menu_buttons):
            button.selected = index == self.selected_index

    def _trigger_menu_action(self, index: int) -> None:
        """Hook point for integration with a larger game flow.

        The current implementation is intentionally lightweight and is meant to be expanded by
        the consuming game state.
        """
        label = self.menu_items[index]
        self.screen_shake = max(self.screen_shake, 2.0)
        if label == "Singleplayer":
            self.running = False
        elif label == "Multiplayer":
            self.running = False
        elif label == "Settings":
            self.running = False
        elif label == "Quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        """Update animated background, menu, and transient effects."""
        self.elapsed += dt
        self._update_button_hover()
        self._update_navigation(dt)

        bg = self.background
        speed_mult = self.config["BACKGROUND"]["star_speed"]
        for star in bg["stars"]:
            star.update(self.width, self.height, speed_mult)

        if self.config["BACKGROUND"]["nebula_enabled"]:
            for cloud in bg["nebula"]:
                cloud.update(self.width, self.height, self.elapsed)

        if self.config["BACKGROUND"]["asteroid_field_enabled"]:
            for asteroid in bg["asteroids"]:
                asteroid.update(self.width, self.height)

        for ship in bg["ships"]:
            if (ship.kind == "xwing" and self.config["SPACE_BATTLE"]["enable_xwings"]) or (
                ship.kind == "tiefighter" and self.config["SPACE_BATTLE"]["enable_tiefighters"]
            ):
                ship.update(self.width, self.height, self.elapsed)
            else:
                ship.y += 0.2
                if ship.y > self.height + 80:
                    ship.reset(self.width, self.height)

        for button in self.menu_buttons:
            button.update(dt)

        if self.screen_shake > 0.05:
            self.screen_shake *= 0.88

    def draw(self) -> None:
        """Render the full menu stack from background to UI."""
        if self.screen is None:
            return

        offset_x = random.uniform(-self.screen_shake, self.screen_shake)
        offset_y = random.uniform(-self.screen_shake, self.screen_shake)
        draw_surface = self.screen
        draw_surface.fill((7, 9, 15))

        self._draw_background(draw_surface)
        self._draw_planets(draw_surface)
        self._draw_battle_ships(draw_surface)
        self._draw_title(draw_surface)
        self._draw_menu(draw_surface)
        self._draw_faction_labels(draw_surface)
        self._draw_vignette(draw_surface)

        if self.screen_shake > 0:
            # The shake is intentionally only a visual effect and is reset after frame updates.
            self.screen_shake *= 0.92

    def _draw_background(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        # Deep space gradient.
        background = pygame.Surface((width, height))
        for y in range(height):
            ratio = y / max(1, height)
            r = int(6 + ratio * 16)
            g = int(10 + ratio * 20)
            b = int(18 + ratio * 30)
            pygame.draw.line(background, (r, g, b), (0, y), (width, y))
        surface.blit(background, (0, 0))

        if self.config["BACKGROUND"]["nebula_enabled"]:
            for cloud in self.background["nebula"]:
                cloud.draw(surface)

        for star in self.background["stars"]:
            star.draw(surface)

        if self.config["BACKGROUND"]["asteroid_field_enabled"]:
            for asteroid in self.background["asteroids"]:
                asteroid.draw(surface)

    def _draw_planets(self, surface: pygame.Surface) -> None:
        for planet in self.planets:
            planet.draw(surface, self.elapsed)

    def _draw_battle_ships(self, surface: pygame.Surface) -> None:
        for ship in self.background["ships"]:
            if ship.kind == "xwing" and self.config["SPACE_BATTLE"]["enable_xwings"]:
                ship.draw(surface, self.elapsed)
            elif ship.kind == "tiefighter" and self.config["SPACE_BATTLE"]["enable_tiefighters"]:
                ship.draw(surface, self.elapsed)

    def _draw_title(self, surface: pygame.Surface) -> None:
        title_cfg = self.config["TITLE"]
        layout = self.config["LAYOUT"]
        pulse = 1.0 + math.sin(self.elapsed * title_cfg["pulse_speed"]) * 0.06

        title_surf = self.fonts["title"].render(title_cfg["text"], True, title_cfg["color"])
        title_glow = self.fonts["title"].render(title_cfg["text"], True, title_cfg["glow_color"])
        subtitle_surf = self.fonts["subtitle"].render(title_cfg["subtitle"], True, (210, 220, 235))

        title_x = int(self.width * layout["title_position"][0])
        title_y = int(self.height * layout["title_position"][1])
        title_rect = title_surf.get_rect(center=(title_x, title_y))

        glow_scale = (title_surf.get_width() * pulse, title_surf.get_height() * pulse)
        title_glow = pygame.transform.smoothscale(title_glow, (int(glow_scale[0] * 1.12), int(glow_scale[1] * 1.12)))

        glow_rect = title_glow.get_rect(center=title_rect.center)
        glow_rect.center = title_rect.center
        surface.blit(title_glow, glow_rect.move(0, 8))
        surface.blit(title_surf, title_rect)

        subtitle_x = int(self.width * layout["subtitle_position"][0])
        subtitle_y = int(self.height * layout["subtitle_position"][1])
        subtitle_rect = subtitle_surf.get_rect(center=(subtitle_x, subtitle_y))
        subtitle_shadow = self.fonts["subtitle"].render(title_cfg["subtitle"], True, (15, 18, 25))
        surface.blit(subtitle_shadow, subtitle_rect.move(0, 2))
        surface.blit(subtitle_surf, subtitle_rect)

    def _draw_menu(self, surface: pygame.Surface) -> None:
        layout = self.config["LAYOUT"]
        center_x = int(self.width * layout["menu_position"][0])
        center_y = int(self.height * layout["menu_position"][1])
        start_y = center_y - ((len(self.menu_buttons) - 1) * 46)

        for index, button in enumerate(self.menu_buttons):
            button_y = start_y + index * 92
            button.draw(surface, center_x, button_y, 1.0)

    def _draw_faction_labels(self, surface: pygame.Surface) -> None:
        layout = self.config["LAYOUT"]
        center_x = int(self.width * layout["faction_position"][0])
        rebel_pos = (
            int(self.width * self.config["FACTIONS"]["logo_offset"][0]),
            int(self.height * self.config["FACTIONS"]["logo_offset"][1]),
        )
        empire_pos = (
            int(self.width * self.config["FACTIONS"]["empire_offset"][0]),
            int(self.height * self.config["FACTIONS"]["empire_offset"][1]),
        )
        rebel_x = rebel_pos[0] - self.rebel_logo.get_width() // 2
        rebel_y = rebel_pos[1] - self.rebel_logo.get_height() // 2

        empire_x = empire_pos[0] - self.empire_logo.get_width() // 2
        empire_y = empire_pos[1] - self.empire_logo.get_height() // 2

        offset = int(math.sin(self.elapsed * self.config["FACTIONS"]["logo_animation_speed"]) * 5)
        surface.blit(self.rebel_logo, (rebel_x + offset, rebel_y + offset))
        surface.blit(self.empire_logo, (empire_x - offset, empire_y - offset))

    def _draw_vignette(self, surface: pygame.Surface) -> None:
        size = surface.get_size()
        vignette = pygame.Surface(size, pygame.SRCALPHA)
        for y in range(size[1]):
            for x in range(size[0]):
                dx = x / max(1, size[0]) - 0.5
                dy = y / max(1, size[1]) - 0.5
                dist = math.sqrt(dx * dx + dy * dy)
                alpha = int(max(0, min(255, dist * 360 * self.config["EFFECTS"]["vignette_strength"])))
                if alpha > 0:
                    vignette.set_at((x, y), (0, 0, 0, alpha))
        surface.blit(vignette, (0, 0))

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events for menu navigation and selection."""
        if event.type == pygame.KEYDOWN:
            keys = {event.key}
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.menu_buttons)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.menu_buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._trigger_menu_action(self.selected_index)
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

            for index, button in enumerate(self.menu_buttons):
                button.selected = index == self.selected_index

        elif event.type == pygame.MOUSEMOTION:
            self._update_button_hover()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.menu_buttons:
                if button.rect and button.rect.collidepoint(event.pos):
                    self.selected_index = button.index
                    self._trigger_menu_action(button.index)
                    break

        elif event.type == pygame.JOYHATMOTION:
            if event.hat[1] > 0:
                self.selected_index = (self.selected_index + 1) % len(self.menu_buttons)
            elif event.hat[1] < 0:
                self.selected_index = (self.selected_index - 1) % len(self.menu_buttons)

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button in (0, 1, 2, 3, 7):
                self._trigger_menu_action(self.selected_index)

    def resize(self, new_size: Tuple[int, int]) -> None:
        """Called when the window dimensions change; recreates layout helpers."""
        self.width, self.height = new_size
        self.background = self._build_background()
        self.planets = self._build_planets()

    def dispose(self) -> None:
        """Release any allocated resources and stop music if active."""
        self.running = False
        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.stop()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Star Wars Inspired Start Screen")
    screen = pygame.display.set_mode((1280, 720))
    start_screen = StartingScreen(screen)
    dt = 1.0 / 60.0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                start_screen.handle_event(event)
        start_screen.update(dt)
        start_screen.draw()
        pygame.display.flip()
        dt = start_screen.clock.tick(60) / 1000.0

    start_screen.dispose()
    pygame.quit()
