"""Erzeugt Referenzwerte aus dem ORIGINAL-Python-Code (deterministische Funktionen), gegen die die C#-Tests prüfen."""
import os, sys, json, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
ROOT = "/home/claude/work/py/Star-Was-Spiel-Python"
os.chdir(ROOT); sys.path.insert(0, ROOT)
import pygame
pygame.init(); pygame.display.set_mode((800, 600))
from game.assets import load_assets
from game.enemies.manager import EnemyManager
from game.enemies.movement import EnemyMovement
from game.enemies.config import ENEMY_ARCHETYPES
from game.entities.ships import XWing, MillenniumFalcon, Tiefighter, BattleDroid
from game.entities.asteroid import Asteroid
from game.constants import DIFFICULTY_SETTINGS

assets = load_assets()
player = XWing(800, 600, assets["x_wing_img"], assets["torpedo_img"])
out = {"manager": [], "movement": [], "ships": [], "asteroid_points": []}

random.uniform = lambda a, b: 1.0   # Zufallsfaktor des Spawn-Intervalls neutralisieren
for diff in DIFFICULTY_SETTINGS:
    em = EnemyManager(800, 600, assets, player, difficulty=diff)
    for sysi in range(0, 6):
        for score in (0, 500, 1000, 1999, 2000, 3500, 4999, 5000, 7500, 9999, 10000, 15000, 40000):
            rec = {"diff": diff, "system": sysi, "score": score,
                   "scale": em._difficulty_scale(score, sysi), "max": em._max_enemies(score, sysi),
                   "interval": em._spawn_interval(score, sysi), "tier": em._unlocked_tier(score), "bal": {}}
            for k, a in ENEMY_ARCHETYPES.items():
                b = em._balanced_archetype(a, score, sysi)
                rec["bal"][k] = {"hp": b.max_hp, "speed": b.max_speed, "acc": b.acceleration, "accuracy": b.accuracy,
                                 "rmin": b.reaction_time[0], "rmax": b.reaction_time[1], "dodge": b.dodge_chance, "torp": b.torpedo_chance}
            out["manager"].append(rec)

class Owner:  # Minimal-Besitzer für EnemyMovement
    centerx = property(lambda s: s.x + s.width * 0.5)
    centery = property(lambda s: s.y + s.height * 0.5)
for arch_key in ("standard", "fast", "heavy", "elite"):
    a = ENEMY_ARCHETYPES[arch_key]
    o = Owner(); o.width = 96; o.height = 96; o.window_width = 800; o.window_height = 600
    o.x = 12.0; o.y = -12.0; o.vx = 0.0; o.vy = 0.0; o.max_speed = a.max_speed; o.acceleration = a.acceleration
    o.hitbox = pygame.Rect(0, 0, 80, 80)
    o.hitbox_offset_x = 5; o.hitbox_offset_y = 5
    o.update_hitbox = lambda: None
    mv = EnemyMovement(o)
    traj = []
    targets = [(500, 200)] * 60 + [(100, 300)] * 60 + [(700, 100)] * 40
    for i, (tx, ty) in enumerate(targets):
        mv.update(1/60, tx, ty, 120.0 if i == 70 else 0.0)
        if i % 10 == 9: traj.append([i, o.x, o.y, o.vx, o.vy])
    out["movement"].append({"arch": arch_key, "traj": traj})

for name, cls, key in (("xwing", XWing, "x_wing_img"), ("milleniumfalcon", MillenniumFalcon, "millennium_falcon_img"),
                       ("tiefighter", Tiefighter, "tie_fighter_img"), ("battledroid", BattleDroid, "battle_droid_img")):
    for moves_left in (0, 7):
        p = cls(800, 600, assets[key], assets["torpedo_img"])
        for _ in range(moves_left): p.move_left()
        t = p.torpedo()
        out["ships"].append({"ship": name, "moves_left": moves_left, "x": p.x, "y": p.y,
            "hitbox": [p.hitbox.x, p.hitbox.y, p.hitbox.w, p.hitbox.h],
            "lasers": [[l.rect.x, l.rect.y, l.rect.w, l.rect.h] for l in p.shoot()],
            "torpedo": None if t is None else [t.rect.x, t.rect.y, t.rect.w, t.rect.h]})
        p2 = cls(800, 600, assets[key], assets["torpedo_img"])
        for _ in range(200): p2.move_right(800)
        out["ships"].append({"ship": name, "moves_left": -1, "x": p2.x, "y": p2.y, "hitbox": [p2.hitbox.x, p2.hitbox.y, p2.hitbox.w, p2.hitbox.h], "lasers": [], "torpedo": None})

random.seed(1)
for size_mul in (0.9, 0.95, 1.0, 1.08):
    for height in (600,):
        for _ in range(40):
            a = Asteroid(800, height, assets["asteroid_images"], size_multiplier=size_mul)
            out["asteroid_points"].append({"mul": size_mul, "scale": a.scale, "points": a.get_points(), "w": a.width, "h": a.height})
json.dump(out, open("/home/claude/work/build/Tests/golden.json", "w"))
print("golden records:", len(out["manager"]), len(out["movement"]), len(out["ships"]), len(out["asteroid_points"]))
