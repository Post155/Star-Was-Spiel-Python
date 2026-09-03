"""Specialized ship classes.

Responsibility:
- Provide specific ship behaviors (shoot, torpedo) and set ship-specific speeds and scales.

Public classes:
- XWing, MillenniumFalcon, Tiefighter, BattleDroid
"""
from .player import Player
from .projectiles import Laser, Torpedo
from game.constants import (
    SHIP_SPEED_XWING,
    SHIP_SPEED_MILLENNIUM,
    SHIP_SPEED_TIEFIGHTER,
    SHIP_SPEED_BATTLEDROID,
    SHIP_SCALE_XWING,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_BATTLEDROID,
)


class XWing(Player):
    def __init__(self, window_width, window_height, x_wing_img, torpedo_img=None):
        super().__init__(x_wing_img, window_width, window_height, SHIP_SCALE_XWING)
        self.speed = SHIP_SPEED_XWING
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.18, self.y + self.height * 0.3)
        l2 = Laser(self.x + self.width * 0.82, self.y + self.height * 0.3)
        return [l1, l2]

    def torpedo(self):
        if self.torpedo_img is None:
            return None
        return Torpedo(self.hitbox.centerx, self.y, self.torpedo_img)


class MillenniumFalcon(Player):
    def __init__(self, window_width, window_height, millennium_falcon_img, torpedo_img=None):
        super().__init__(millennium_falcon_img, window_width, window_height, SHIP_SCALE_MILLENNIUM)
        self.speed = SHIP_SPEED_MILLENNIUM
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.43, self.y + self.height * 0.06)
        l2 = Laser(self.x + self.width * 0.58, self.y + self.height * 0.06)
        return [l1, l2]

    def torpedo(self):
        return None


class Tiefighter(Player):
    def __init__(self, window_width, window_height, tie_fighter_img, torpedo_img=None):
        super().__init__(tie_fighter_img, window_width, window_height, SHIP_SCALE_TIEFIGHTER)
        self.speed = SHIP_SPEED_TIEFIGHTER
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.44, self.y + self.height * 0.30)
        l2 = Laser(self.x + self.width * 0.55, self.y + self.height * 0.30)
        return [l1, l2]

    def torpedo(self):
        if self.torpedo_img is None:
            return None
        return Torpedo(self.x + self.width * 0.47, self.y + self.height * 0.12, self.torpedo_img)


class BattleDroid(Player):
    def __init__(self, window_width, window_height, battle_droid_img, torpedo_img=None):
        super().__init__(battle_droid_img, window_width, window_height, SHIP_SCALE_BATTLEDROID)
        self.speed = SHIP_SPEED_BATTLEDROID
        self.torpedo_img = torpedo_img

    def shoot(self):
        l1 = Laser(self.x + self.width * 0.05, self.y + self.height * 0.01)
        l2 = Laser(self.x + self.width * 0.94, self.y + self.height * 0.01)
        return [l1, l2]

    def torpedo(self):
        return None
