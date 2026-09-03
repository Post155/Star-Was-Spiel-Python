"""StarField subsystem: manage star layers (spawn, update, render).

Responsibility:
- Initialize star layers according to density/tint
- Update star positions
- Draw stars
"""
from typing import List, Optional
import pygame
from .objects import Star


class StarField:
    def __init__(self, width: int, height: int, density: float = 1.0, tint: Optional[tuple] = None) -> None:
        self.width = width
        self.height = height
        self.density = max(0.1, float(density))
        self.tint = tint

        self.layer1: List[Star] = []
        self.layer2: List[Star] = []

        self._init_star_layers()

    def _desired_counts(self) -> (int, int):
        desired1 = max(50, int((self.width * self.height) / 6000 * self.density))
        desired2 = max(20, int((self.width * self.height) / 12000 * self.density))
        return desired1, desired2

    def _init_star_layers(self) -> None:
        d1, d2 = self._desired_counts()
        self.layer1 = [Star(self.width, self.height, layer=1) for _ in range(d1)]
        self.layer2 = [Star(self.width, self.height, layer=2, tint=self.tint) for _ in range(d2)]

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._init_star_layers()

    def update(self) -> None:
        for star in self.layer1:
            star.update()
        for star in self.layer2:
            star.update()

    def draw(self, screen: pygame.Surface) -> None:
        for star in self.layer1:
            star.draw(screen)
        for star in self.layer2:
            star.draw(screen)

    def set_visuals(self, density: float, tint: Optional[tuple]) -> None:
        """Adjust visual parameters and reinitialize if changed."""
        changed = False
        if abs(self.density - density) > 1e-6:
            self.density = density
            changed = True
        if self.tint != tint:
            self.tint = tint
            changed = True
        if changed:
            self._init_star_layers()
