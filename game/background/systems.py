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
    """Build star systems and assign discovered planets to canonical systems.

    The function prefers canonical mappings for known Star Wars planets. Any
    discovered planet images are included as planet-level entries in their
    proper system. If an expected planet image is missing the system still
    exists but without that planet.
    """

    # Helper to check if an asset for a planet exists
    def has_asset(key: str) -> bool:
        if not assets:
            return False
        return (assets.get(f'{key}_img') is not None) or (assets.get(key) is not None)

    systems: List[StarSystem] = []

    systems.append(StarSystem(
        'EARTH',
        ['EARTH', 'Milky-System'],
        planet_keys=['earth'] if has_asset('earth') else [],
        star_tint=(200, 120, 80),
        star_density=0.5,
        asteroid_speed_mul=0.5,
        difficulty=1,
        visual_filter=(80, 20, 8, 28),
    ))

    systems.append(StarSystem(
        'SATURN',
        ['SATURN', 'Milky-System'],
        planet_keys=['saturn'] if has_asset('saturn') else [],
        star_tint=(200, 120, 80),
        star_density=0.6,
        asteroid_speed_mul=1.3,
        difficulty=2,
        visual_filter=(80, 20, 8, 28),
    ))    

    systems.append(StarSystem(
        'BLACKHOLE',
        ['BLACKHOLE', 'ERROR'],
        planet_keys=['blackhole'] if has_asset('blackhole') else [],
        star_tint=(200, 120, 80),
        star_density=2.0,
        asteroid_speed_mul=2.5,
        difficulty=5,
        visual_filter=(80, 20, 8, 28),
    )) 

    systems.append(StarSystem(
        'TODESSTERN',
        ['TODESSTERN', 'Somewhere'],
        planet_keys=['todesstern'] if has_asset('todesstern') else [],
        star_tint=(200, 120, 80),
        star_density=2.0,
        asteroid_speed_mul=2.0,
        difficulty=4,
        visual_filter=(80, 20, 8, 28),
    )) 

    systems.append(StarSystem(
        'STERNZERSTÖRER',
        ['STERNZERSTÖRER', 'Somewhere'],
        planet_keys=['sternzerstörer'] if has_asset('sternzerstörer') else [],
        star_tint=(200, 120, 80),
        star_density=2.0,
        asteroid_speed_mul=2.0,
        difficulty=4,
        visual_filter=(80, 20, 8, 28),
    )) 

    systems.append(StarSystem(
        'TATOOINE',
        ['TATOOINE', 'Tatooine-System'],
        planet_keys=['tatooine'] if has_asset('tatooine') else [],
        foreground_keys=['sun_1', 'sun_2'] if has_asset('sun_1') else [],
        star_tint=(255, 230, 160),
        star_density=0.9,
        asteroid_speed_mul=1.25,
        difficulty=2,
        visual_filter=(30, 20, 0, 20),
    ))

    systems.append(StarSystem(
        'PURPLE',
        ['PURPLE', 'Strange-Sektor'],
        planet_keys=['purple'] if has_asset('purple') else [],
        star_tint=(180, 200, 220),
        star_density=0.9,
        asteroid_speed_mul=1.5,
        difficulty=2,
        visual_filter=(16, 24, 60, 12),
    ))

    systems.append(StarSystem(
        'KAMINO',
        ['KAMINO', 'Kamino-System'],
        planet_keys=['kamino'] if has_asset('kamino') else [],
        star_tint=(160, 200, 230),
        star_density=1.05,
        asteroid_speed_mul=1.2,
        difficulty=2,
        visual_filter=(12, 24, 36, 10),
    ))

    systems.append(StarSystem(
        'HOTH',
        ['HOTH', 'Hoth-System'],
        planet_keys=['hoth'] if has_asset('hoth') else [],
        star_tint=(200, 220, 255),
        star_density=1.1,
        asteroid_speed_mul=1.4,
        difficulty=2,
        visual_filter=(8, 16, 40, 28),
    ))

    systems.append(StarSystem(
        'ENDOR',
        ['ENDOR', 'Endor-System'],
        planet_keys=['endor'] if has_asset('endor') else [],
        star_tint=(180, 230, 180),
        star_density=1.25,
        asteroid_speed_mul=1.6,
        extra_flags={'more_enemies': True},
        difficulty=3,
        visual_filter=(10, 30, 12, 24),
    ))

    systems.append(StarSystem(
        'CORUSCANT',
        ['CORUSCANT', 'Coruscant-System'],
        planet_keys=['coruscant'] if has_asset('coruscant') else (['corusant'] if has_asset('corusant') else []),
        star_tint=(220, 210, 200),
        star_density=0.8,
        asteroid_speed_mul=1.15,
        difficulty=3,
        visual_filter=(40, 30, 30, 18),
    ))

    systems.append(StarSystem(
        'MUSTAFAR',
        ['MUSTAFAR', 'Mustafar-System'],
        planet_keys=['mustafar'] if has_asset('mustafar') else [],
        star_tint=(200, 120, 80),
        star_density=0.9,
        asteroid_speed_mul=1.6,
        difficulty=3,
        visual_filter=(80, 20, 8, 28),
    ))

    return systems
