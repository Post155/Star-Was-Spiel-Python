import pygame

from game.constants import ASSET_PATHS


def set_window_icon(icon_path=None):
    """Apply the configured game icon to the current window and taskbar."""
    if icon_path is None:
        icon_path = ASSET_PATHS['window_icon']

    icon = pygame.image.load(icon_path).convert_alpha()
    pygame.display.set_icon(icon)
    return icon


def load_assets():
    """Load and return all game images as a dict. Call after pygame.init()."""
    assets = {}

    assets['window_icon_img'] = pygame.image.load(ASSET_PATHS['window_icon'])
    assets['x_wing_img'] = pygame.image.load(ASSET_PATHS['x_wing']).convert_alpha()
    assets['millennium_falcon_img'] = pygame.image.load(ASSET_PATHS['millennium_falcon']).convert_alpha()
    assets['tie_fighter_img'] = pygame.image.load(ASSET_PATHS['tie_fighter']).convert_alpha()
    assets['asteroid_images'] = [
        pygame.image.load(path).convert_alpha() for path in ASSET_PATHS['asteroid_frames']
    ]
    assets['torpedo_img'] = pygame.image.load(ASSET_PATHS['torpedo']).convert_alpha()
    assets['explosion_img'] = pygame.image.load(ASSET_PATHS['explosion']).convert_alpha()

    return assets
