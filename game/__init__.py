"""Star Wars game package.

This package keeps the original gameplay code intact while now exposing a
cleaner bootstrap and configuration surface for the refactored structure.
"""

from game.config import DEFAULT_DIFFICULTY, VALID_DIFFICULTIES, normalize_difficulty
from game.settings import DEFAULT_SETTINGS, load_settings, save_settings

__all__ = [
    "DEFAULT_DIFFICULTY",
    "VALID_DIFFICULTIES",
    "DEFAULT_SETTINGS",
    "load_settings",
    "save_settings",
    "normalize_difficulty",
]
