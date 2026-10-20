"""Small compatibility layer for the application bootstrap.

The original game still lives in game/StarWarsGame.py. This module exposes a
clean entry point for the newer modular structure without reimplementing the
existing gameplay loop.
"""
from __future__ import annotations

import pygame

from game.assets import load_assets, set_window_icon
from game.settings import load_settings


class GameApplication:
    """Minimal application shell used by the modular structure."""

    def __init__(self, width: int = 800, height: int = 600, title: str = "Star Wars") -> None:
        self.width = width
        self.height = height
        self.title = title
        self.settings = load_settings()
        flags = pygame.FULLSCREEN if self.settings.get("fullscreen", False) else pygame.RESIZABLE
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.title)
        set_window_icon()
        self.assets = load_assets()

    def run(self):
        from game.StarWarsGame import main

        return main()


def run_game():
    """Run the project's original game loop through the modular bootstrap."""
    from game.StarWarsGame import main

    return main()
