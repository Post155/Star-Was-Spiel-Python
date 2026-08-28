import pygame

from game.assets import set_window_icon


def resize_and_refresh(screen, width, height):
    """Create a resizeable window and keep the icon consistent."""
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    set_window_icon()
    return screen
