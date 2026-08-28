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


def build_systems(assets: Optional[dict] = None) -> List[StarSystem]:
    systems = [
        StarSystem(
            'CORE WORLDS',
            ['SYSTEMWECHSEL', 'CORE WORLDS'],
            planet_keys=['earth', 'coruscant', 'satellites'],
            foreground_keys=[],
            star_tint=None,
            star_density=1.0,
            asteroid_speed_mul=1.0,
        ),
        StarSystem(
            'TATOOINE',
            ['WARNUNG', 'TATOOINE-SEKTOR ERREICHT'],
            planet_keys=['tatooine_planet'],
            foreground_keys=['sun_1', 'sun_2'],
            star_tint=(255, 230, 160),
            star_density=0.9,
            asteroid_speed_mul=1.25,
            nebula_keys=['gelber_nebel'],
        ),
        StarSystem(
            'HOTH',
            ['WARNUNG', 'HOTH-SEKTOR ERREICHT'],
            planet_keys=['hoth_planet'],
            star_tint=(200, 220, 255),
            star_density=1.1,
            asteroid_speed_mul=0.95,
            nebula_keys=['blue_nebula'],
        ),
        StarSystem(
            'ENDOR',
            ['WARNUNG', 'ENDOR-SEKTOR ERREICHT'],
            planet_keys=['endor', 'forest_moon'],
            star_tint=(180, 230, 180),
            star_density=1.3,
            asteroid_speed_mul=1.0,
            extra_flags={'more_enemies': True},
        ),
        StarSystem(
            'DEATH STAR SECTOR',
            ['WARNUNG', 'IMPERIALER RAUM'],
            planet_keys=['death_star', 'imperial_station', 'star_destroyer'],
            star_tint=(120, 120, 120),
            star_density=0.6,
            asteroid_speed_mul=0.8,
            extra_flags={'imperial_presence': True},
        ),
        StarSystem(
            'NEBULA',
            ['WARNUNG', 'NEBELSEKTOR ERREICHT'],
            nebula_keys=['nebula_red', 'nebula_blue', 'nebula_purple'],
            star_tint=None,
            star_density=1.0,
            asteroid_speed_mul=0.9,
        ),
        StarSystem(
            'KRIEGSGEBIET',
            ['WARNUNG', 'AKTIVE KRIEGSZONE'],
            foreground_keys=['star_destroyer', 'xwing_squadron', 'tie_fighter', 'battle_explosion'],
            star_tint=None,
            star_density=0.8,
            asteroid_speed_mul=1.0,
            extra_flags={'battle': True},
        ),
    ]
    return systems
