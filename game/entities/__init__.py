"""Public exports for the game.entities package.

This module re-exports the core entity classes so existing imports
`from game.entities import Asteroid, XWing, ...` continue to work.

Responsibility:
- Provide a stable public API for entity types (Asteroid, Laser, Torpedo, Explosion, Player, XWing, MillenniumFalcon, Tiefighter, BattleDroid)
"""
from .asteroid import Asteroid
from .projectiles import Laser, Torpedo
from .explosion import Explosion
from .player import Player, Spieler  # Spieler kept as alias for compatibility
from .ships import XWing, MillenniumFalcon, Tiefighter, BattleDroid

__all__ = [
    'Asteroid', 'Laser', 'Torpedo', 'Explosion', 'Player', 'Spieler',
    'XWing', 'MillenniumFalcon', 'Tiefighter', 'BattleDroid'
]
