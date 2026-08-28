import os

import pygame

from game.constants import ASSET_PATHS


PLANET_NAME_ALIASES = {
    'earth': 'earth',
    'coruscant': 'corusant',
    'satellites': 'saturn',
    'tatooine_planet': 'tatooine',
    'hoth_planet': 'hoth',
    'endor': 'endor',
    'forest_moon': 'endor',
    'death_star': 'todesstern',
    'imperial_station': 'imperial_station',
    'star_destroyer': 'sternzerstoerer',
}


def set_window_icon(icon_path=None):
    """Apply the configured game icon to the current window and taskbar."""
    if icon_path is None:
        icon_path = ASSET_PATHS['window_icon']

    try:
        icon = pygame.image.load(icon_path).convert_alpha()
        pygame.display.set_icon(icon)
        return icon
    except Exception:
        return None


def _safe_load(path, convert_alpha=True):
    try:
        if not pygame.display.get_init():
            pygame.display.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))

        surf = pygame.image.load(path)
        return surf.convert_alpha() if convert_alpha else surf.convert()
    except Exception:
        return None


def _normalize_asset_name(name):
    value = name.lower().replace('.png', '').replace('.jpg', '')
    value = value.replace('planet_', '')
    value = value.replace('-', '').replace(' ', '')
    value = value.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
    value = value.replace('ß', 'ss')
    return value


def _load_planet_assets():
    planet_dir = os.path.join('Pixelarts', 'Planets')
    discovered = {}

    if not os.path.isdir(planet_dir):
        return discovered

    for root, _, files in os.walk(planet_dir):
        for filename in files:
            if not filename.lower().endswith('.png'):
                continue
            full_path = os.path.join(root, filename)
            img = _safe_load(full_path)
            if img is None:
                continue

            normalized = _normalize_asset_name(filename)
            discovered[normalized] = img
            discovered[f'{normalized}_img'] = img

            if filename.lower().startswith('planet_'):
                key = _normalize_asset_name(filename[len('planet_'):])
                discovered[key] = img
                discovered[f'{key}_img'] = img

    return discovered


def load_assets():
    """Load and return all game images as a dict. Call after pygame.init()."""
    assets = {}

    assets['window_icon_img'] = _safe_load(ASSET_PATHS.get('window_icon'))
    assets['x_wing_img'] = _safe_load(ASSET_PATHS.get('x_wing'))
    assets['millennium_falcon_img'] = _safe_load(ASSET_PATHS.get('millennium_falcon'))
    assets['tie_fighter_img'] = _safe_load(ASSET_PATHS.get('tie_fighter'))
    assets['battle_droid_img'] = _safe_load(ASSET_PATHS.get('battle_droid'))
    assets['rebel_logo_img'] = _safe_load(ASSET_PATHS.get('rebel_logo'))
    assets['empire_logo_img'] = _safe_load(ASSET_PATHS.get('empire_logo'))

    asteroid_frames = ASSET_PATHS.get('asteroid_frames', [])
    assets['asteroid_images'] = [img for img in (_safe_load(p) for p in asteroid_frames) if img]

    assets['torpedo_img'] = _safe_load(ASSET_PATHS.get('torpedo'))
    assets['explosion'] = _safe_load(ASSET_PATHS.get('explosion'))
    assets['explosion_img'] = assets['explosion']

    # load system/planet assets if available
    system_keys = [
        'earth', 'coruscant', 'satellites',
        'tatooine_planet', 'sun_1', 'sun_2', 'gelber_nebel',
        'hoth_planet', 'blue_nebula',
        'endor', 'forest_moon',
        'death_star', 'imperial_station', 'star_destroyer',
        'nebula_red', 'nebula_blue', 'nebula_purple',
        'xwing_squadron', 'tie_fighter', 'battle_explosion'
    ]

    for key in system_keys:
        path = ASSET_PATHS.get(key)
        if path:
            assets[f'{key}_img'] = _safe_load(path)

    discovered_planets = _load_planet_assets()
    for key, value in discovered_planets.items():
        assets[key] = value

    for key, asset_name in PLANET_NAME_ALIASES.items():
        alias_key = _normalize_asset_name(asset_name)
        if alias_key in discovered_planets:
            assets[f'{key}_img'] = discovered_planets[alias_key]

    planet_images = []
    for image in discovered_planets.values():
        if image not in planet_images:
            planet_images.append(image)

    if not planet_images:
        for p in ("Pixelarts/Planets/planet_blue.png", "Pixelarts/Planets/planet_orange.png", "Pixelarts/Planets/planet_gray.png"):
            img = _safe_load(p)
            if img:
                planet_images.append(img)

    assets['planet_images'] = planet_images
    return assets
