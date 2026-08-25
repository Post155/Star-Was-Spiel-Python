import pygame

from game.constants import ASSET_PATHS


def load_assets():
    """Load and return all game images as a dict. Call after pygame.init()."""
    assets = {}

    assets['x_wing_img'] = pygame.image.load(ASSET_PATHS['x_wing']).convert_alpha()
    assets['millennium_falcon_img'] = pygame.image.load(ASSET_PATHS['millennium_falcon']).convert_alpha()
    assets['asteroid_images'] = [
        pygame.image.load(path).convert_alpha() for path in ASSET_PATHS['asteroid_frames']
    ]
    assets['torpedo_img'] = pygame.image.load(ASSET_PATHS['torpedo']).convert_alpha()
    assets['explosion_img'] = pygame.image.load(ASSET_PATHS['explosion']).convert_alpha()

    return assets
