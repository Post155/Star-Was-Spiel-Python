"""PlanetManager: spawn, update and draw planets for the current system.

Responsibility:
- Ensure one planet per system (configurable)
- Spawn planets when allowed and respecting entry/exit delays
- Update planetary motion and removal
- Expose simple interface for coordinator BackgroundManager
"""
from typing import List, Optional, Tuple
import random
import pygame
from .objects import Planet


class PlanetManager:
    def __init__(self, width: int, height: int, assets: Optional[dict] = None) -> None:
        self.width = width
        self.height = height
        self.assets = assets or {}

        self.planets: List[Planet] = []

        # config per-system (set by coordinator)
        self.planet_images: List[pygame.Surface] = []
        self.planet_max_visible: int = 1
        self.spawn_cooldown_range: Tuple[int, int] = (500, 1000)
        self.speed_range: Tuple[float, float] = (0.4, 0.7)
        self.linger_range: Tuple[int, int] = (5000, 7000)

        self.planet_spawned_this_system = False
        self.spawn_cooldown = 0

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        for p in self.planets:
            p.width = width
            p.height = height

    def set_system_planet_settings(self, images: List[pygame.Surface], max_visible: int,
                                   spawn_range: Tuple[int, int], speed_range: Tuple[float, float], linger_range: Tuple[int, int]) -> None:
        self.planet_images = images[:]
        self.planet_max_visible = max_visible
        self.spawn_cooldown_range = spawn_range
        self.speed_range = speed_range
        self.linger_range = linger_range
        self.spawn_cooldown = 0
        self.planet_spawned_this_system = False

    def _can_spawn(self, candidate: Planet) -> bool:
        for existing in self.planets:
            if existing.is_exiting:
                continue
            if candidate.get_rect().colliderect(existing.get_rect()):
                return False
        return True

    def maybe_spawn(self, allow_planets: bool) -> None:
        """Attempt to spawn a planet if allowed by timing and configuration."""
        if not allow_planets:
            return

        if self.spawn_cooldown > 0:
            self.spawn_cooldown = max(0, self.spawn_cooldown - 1)
            return

        if (not self.planet_images) or self.planet_spawned_this_system:
            return

        # simple spawn of a single planet for the system
        img = random.choice(self.planet_images)
        planet = Planet(img, self.width, self.height, speed_range=self.speed_range, linger_range=self.linger_range)
        if self._can_spawn(planet):
            self.planets.append(planet)
            self.planet_spawned_this_system = True
            self.spawn_cooldown = random.randint(self.spawn_cooldown_range[0], self.spawn_cooldown_range[1])

    def update(self) -> None:
        for p in self.planets[:]:
            p.update()
            if p.expired():
                try:
                    self.planets.remove(p)
                except ValueError:
                    pass

    def draw(self, screen: pygame.Surface) -> None:
        for p in self.planets:
            p.draw(screen)

    def clear_all(self) -> None:
        self.planets.clear()
        self.planet_spawned_this_system = False
        self.spawn_cooldown = 0

    def start_exit_all(self) -> None:
        for p in self.planets:
            p.is_exiting = True
            try:
                p.speed = max(p.speed, 2.0)
            except Exception:
                pass

    def mark_system_started(self) -> None:
        self.planet_spawned_this_system = False
        self.spawn_cooldown = 0
