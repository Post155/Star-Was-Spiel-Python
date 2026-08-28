"""Highscore persistence using a JSON file.

Stores a single value under the key "highscore" in a file located next to this module
(game/highscore.json). Provides simple load/save helpers and tolerates missing or
malformed files by returning 0 as a safe default.
"""

import os
import json

_HS_FILENAME = os.path.join(os.path.dirname(__file__), "highscore.json")


def load_highscore():
    """Load the stored highscore. Returns 0 if no valid score is found."""
    try:
        with open(_HS_FILENAME, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            try:
                return int(data.get("highscore", 0))
            except (TypeError, ValueError):
                return 0
    except FileNotFoundError:
        return 0
    except (json.JSONDecodeError, OSError):
        # If the file is corrupted or unreadable, treat it as no highscore.
        return 0


def save_highscore(score):
    """Save the given score as the new highscore (overwrites previous value).

    score is coerced to int. The function creates the file if necessary.
    """
    try:
        os.makedirs(os.path.dirname(_HS_FILENAME), exist_ok=True)
        with open(_HS_FILENAME, "w", encoding="utf-8") as fh:
            json.dump({"highscore": int(score)}, fh)
    except OSError:
        # If writing fails (permissions, disk issues), fail silently to avoid
        # breaking game flow. The caller may handle logging if needed.
        pass
