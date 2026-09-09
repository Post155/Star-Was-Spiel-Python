"""Enemy configuration and ship-opposition rules.

The data in this module deliberately contains no pygame logic. New variants,
bosses or faction rules can be added here without touching the main game loop.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from game.constants import (
    SHIP_SCALE_BATTLEDROID,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_XWING,
)


@dataclass(frozen=True)
class EnemyArchetype:
    key: str
    display_name: str
    max_hp: int
    max_speed: float
    acceleration: float
    armor_resistance: float
    laser_damage: int
    laser_cooldown: Tuple[float, float]
    burst_range: Tuple[int, int]
    accuracy: float
    reaction_time: Tuple[float, float]
    dodge_chance: float
    torpedo_damage: int
    torpedo_cooldown: Tuple[float, float]
    torpedo_chance: float
    base_score: int
    bonus_score: Tuple[int, int]
    visual_scale_multiplier: float = 1.0


ENEMY_ARCHETYPES: Dict[str, EnemyArchetype] = {
    "standard": EnemyArchetype(
        key="standard",
        display_name="STANDARD",
        max_hp=4,
        max_speed=185.0,
        acceleration=520.0,
        armor_resistance=0.00,
        laser_damage=1,
        laser_cooldown=(1.10, 1.75),
        burst_range=(1, 2),
        accuracy=0.68,
        reaction_time=(0.26, 0.48),
        dodge_chance=0.36,
        torpedo_damage=2,
        torpedo_cooldown=(10.0, 14.0),
        torpedo_chance=0.14,
        base_score=100,
        bonus_score=(0, 45),
    ),
    "fast": EnemyArchetype(
        key="fast",
        display_name="SCHNELL",
        max_hp=3,
        max_speed=285.0,
        acceleration=760.0,
        armor_resistance=0.00,
        laser_damage=1,
        laser_cooldown=(0.78, 1.30),
        burst_range=(1, 3),
        accuracy=0.61,
        reaction_time=(0.16, 0.31),
        dodge_chance=0.58,
        torpedo_damage=2,
        torpedo_cooldown=(9.0, 13.0),
        torpedo_chance=0.18,
        base_score=190,
        bonus_score=(25, 90),
        visual_scale_multiplier=0.88,
    ),
    "heavy": EnemyArchetype(
        key="heavy",
        display_name="SCHWER",
        max_hp=10,
        max_speed=125.0,
        acceleration=310.0,
        armor_resistance=0.28,
        laser_damage=2,
        laser_cooldown=(1.20, 1.85),
        burst_range=(2, 3),
        accuracy=0.74,
        reaction_time=(0.38, 0.62),
        dodge_chance=0.22,
        torpedo_damage=2,
        torpedo_cooldown=(8.0, 11.5),
        torpedo_chance=0.34,
        base_score=340,
        bonus_score=(55, 160),
        visual_scale_multiplier=1.18,
    ),
    "elite": EnemyArchetype(
        key="elite",
        display_name="ELITE",
        max_hp=8,
        max_speed=250.0,
        acceleration=680.0,
        armor_resistance=0.14,
        laser_damage=2,
        laser_cooldown=(0.58, 0.96),
        burst_range=(2, 4),
        accuracy=0.91,
        reaction_time=(0.10, 0.20),
        dodge_chance=0.84,
        torpedo_damage=2,
        torpedo_cooldown=(5.8, 8.4),
        torpedo_chance=0.58,
        base_score=650,
        bonus_score=(110, 320),
        visual_scale_multiplier=1.05,
    ),
}


# Exact rule requested by the game design. The values are asset keys.
OPPOSING_SHIP_BY_PLAYER = {
    "XWing": "tie_fighter_img",
    "MillenniumFalcon": "battle_droid_img",
    "Tiefighter": "x_wing_img",
    "BattleDroid": "millennium_falcon_img",
}

SHIP_NAME_BY_ASSET = {
    "tie_fighter_img": "TieFighter",
    "battle_droid_img": "BattleDroid",
    "x_wing_img": "XWing",
    "millennium_falcon_img": "MillenniumFalcon",
}

SHIP_SCALE_BY_ASSET = {
    "tie_fighter_img": SHIP_SCALE_TIEFIGHTER,
    "battle_droid_img": SHIP_SCALE_BATTLEDROID,
    "x_wing_img": SHIP_SCALE_XWING,
    "millennium_falcon_img": SHIP_SCALE_MILLENNIUM,
}


def opposing_ship_asset_key(player) -> str:
    """Return the only allowed enemy ship model for *player*."""
    class_name = player.__class__.__name__
    try:
        return OPPOSING_SHIP_BY_PLAYER[class_name]
    except KeyError as exc:
        raise ValueError(f"Unbekannter Spielerschiff-Typ: {class_name}") from exc
