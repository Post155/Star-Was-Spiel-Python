"""Liest mit ECHTEM Pygame (headless) die exakten Sprite-Metriken des Originals aus.
Ergebnis: JSON mit Schiffsgrößen, Alpha-Hitboxen, Gegner-Hitboxen je Archetyp, Asteroid-Frames usw."""
import os, sys, json
os.environ["SDL_VIDEODRIVER"] = "dummy"
ROOT = "/home/claude/work/py/Star-Was-Spiel-Python"
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from game.assets import load_assets
from game.entities.ships import XWing, MillenniumFalcon, Tiefighter, BattleDroid
from game.enemies.base import EnemyBase
from game.enemies.config import ENEMY_ARCHETYPES, SHIP_SCALE_BY_ASSET
from game.constants import normalize_ship_scale
from game.background.systems import build_systems

assets = load_assets()
out = {"images": {}, "ships": {}, "enemies": {}, "asteroid_frames": [], "systems": [], "asset_keys_found": sorted(k for k,v in assets.items() if v is not None and not isinstance(v, list))}

def size(img): return list(img.get_size()) if img is not None else None
for key in ["x_wing_img","millennium_falcon_img","tie_fighter_img","battle_droid_img","torpedo_img","explosion_img","rebel_logo_img","empire_logo_img","lightsaber_blue_img","lightsaber_red_img"]:
    out["images"][key] = size(assets.get(key))
out["asteroid_frames"] = [list(i.get_size()) for i in assets["asteroid_images"]]

ships = {"xwing": (XWing, "x_wing_img"), "milleniumfalcon": (MillenniumFalcon, "millennium_falcon_img"),
         "tiefighter": (Tiefighter, "tie_fighter_img"), "battledroid": (BattleDroid, "battle_droid_img")}
for name, (cls, key) in ships.items():
    p = cls(800, 600, assets[key], assets["torpedo_img"])
    laser = p.shoot()
    tor = p.torpedo()
    out["ships"][name] = {
        "scale": p.scale, "width": p.width, "height": p.height, "speed": p.speed,
        "x": p.x, "y": p.y,
        "hitbox_offset": [p.hitbox_offset_x, p.hitbox_offset_y], "hitbox_size": [p.hitbox.width, p.hitbox.height],
        "lasers": [[l.rect.x - p.x, l.rect.y - p.y] for l in laser],
        "torpedo": None if tor is None else {"rect": [tor.rect.x, tor.rect.y, tor.rect.width, tor.rect.height],
                                              "rel": [tor.rect.x - p.x, tor.rect.y - p.y], "size": list(tor.image.get_size())},
    }

# Gegner-Metriken (pro Spielerschiff -> Gegnerbild, pro Archetyp)
for player_cls, asset_key in [("XWing","tie_fighter_img"),("MillenniumFalcon","battle_droid_img"),("Tiefighter","x_wing_img"),("BattleDroid","millennium_falcon_img")]:
    out["enemies"][player_cls] = {"asset": asset_key, "archetypes": {}}
    for a_key, arch in ENEMY_ARCHETYPES.items():
        e = EnemyBase(assets[asset_key], "x", arch, 800, 600, 100, 20, SHIP_SCALE_BY_ASSET[asset_key], torpedo_image=assets["torpedo_img"])
        out["enemies"][player_cls]["archetypes"][a_key] = {
            "visual_scale": e.visual_scale, "width": e.width, "height": e.height,
            "hitbox_offset": [e.hitbox_offset_x, e.hitbox_offset_y], "hitbox_size": [e.hitbox.width, e.hitbox.height]}

# Planeten: welche Systeme haben im Original wirklich ein Planetenbild?
for s in build_systems(assets):
    out["systems"].append({"id": s.id_name, "planet_keys": s.planet_keys, "foreground_keys": s.foreground_keys,
        "star_tint": s.star_tint, "star_density": s.star_density, "asteroid_speed_mul": s.asteroid_speed_mul,
        "difficulty": s.difficulty, "visual_filter": list(s.visual_filter), "display_lines": s.display_lines, "extra_flags": s.extra_flags})
out["planet_images"] = [list(i.get_size()) for i in assets["planet_images"]]

# Rundungsverhalten von scale_by
test = pygame.Surface((101, 53), pygame.SRCALPHA)
out["scale_by_probe"] = {f"{f}": list(pygame.transform.scale_by(test, f).get_size()) for f in (0.25, 0.5, 0.75, 0.9, 1.0, 0.95*0.75, 0.18, 1.25, 0.42, 0.9*1.08)}

# Planet-Dateien und Normalisierung
from game.assets import _normalize_asset_name
out["planet_files"] = {}
for root, _, files in os.walk("Pixelarts/Planets"):
    for f in files:
        if f.lower().endswith(".png"):
            img = pygame.image.load(os.path.join(root, f))
            out["planet_files"][os.path.join(root, f)] = {"normalized": _normalize_asset_name(f), "size": list(img.get_size())}
json.dump(out, open("/home/claude/work/notes/metrics.json", "w"), indent=1, ensure_ascii=False)
print("OK")
