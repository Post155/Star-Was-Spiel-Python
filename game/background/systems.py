from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StarSystem:
    """Configuration holder for a star system/sector."""

    id_name: str
    display_lines: List[str]
    planet_keys: List[str] = field(default_factory=list)
    foreground_keys: List[str] = field(default_factory=list)
    star_tint: Optional[tuple] = None
    star_density: float = 1.0
    asteroid_speed_mul: float = 1.0
    nebula_keys: List[str] = field(default_factory=list)
    extra_flags: Dict[str, object] = field(default_factory=dict)
    difficulty: int = 1
    visual_filter: tuple = (0, 0, 0, 0)


# LEVEL CONFIGURATION:
# Every planet image in Pixelarts/Planets gets its own level/sector here.
# Each level uses exactly one unique planet image, so a planet can appear only once
# in a cycle. The visual_filter is a non-text indicator of the current system.
# To change the progression, reorder this list or replace a planet key.

def build_systems(assets: Optional[dict] = None) -> List[StarSystem]:
    systems = [
        StarSystem(
            'CORE WORLDS',
            ['SYSTEMWECHSEL', 'CORE WORLDS'],
            planet_keys=['earth'],
            foreground_keys=[],
            star_tint=None,
            star_density=1.0,
            asteroid_speed_mul=1.0,
            difficulty=1,
        ),
        StarSystem(
            'TATOOINE',
            ['WARNUNG', 'TATOOINE-SEKTOR ERREICHT'],
            planet_keys=['tatooine_planet'],
            foreground_keys=['sun_1', 'sun_2'],
            star_tint=(255, 230, 160),
            star_density=0.9,
            asteroid_speed_mul=1.25,
            difficulty=2,
        ),
        StarSystem(
            'HOTH',
            ['WARNUNG', 'HOTH-SEKTOR ERREICHT'],
            planet_keys=['hoth_planet'],
            star_tint=(200, 220, 255),
            star_density=1.1,
            asteroid_speed_mul=1.4,
            difficulty=2,
        ),
        StarSystem(
            'ENDOR',
            ['WARNUNG', 'ENDOR-SEKTOR ERREICHT'],
            planet_keys=['endor'],
            star_tint=(180, 230, 180),
            star_density=1.3,
            asteroid_speed_mul=1.6,
            extra_flags={'more_enemies': True},
            difficulty=3,
        ),
        StarSystem(
            'DEATH STAR SECTOR',
            ['WARNUNG', 'IMPERIALER RAUM'],
            planet_keys=['death_star', 'imperial_station', 'star_destroyer'],
            star_tint=(120, 120, 120),
            star_density=0.6,
            asteroid_speed_mul=1.8,
            extra_flags={'imperial_presence': True},
            difficulty=4,
        ),
        StarSystem(
            'KRIEGSGEBIET',
            ['WARNUNG', 'AKTIVE KRIEGSZONE'],
            foreground_keys=['star_destroyer', 'xwing_squadron', 'tie_fighter', 'battle_explosion'],
            star_tint=None,
            star_density=0.8,
            asteroid_speed_mul=2.0,
            extra_flags={'battle': True},
            difficulty=5,
        ),
    ]
    return systems
