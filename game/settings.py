"""Persistent user settings for the Star Wars game."""
from __future__ import annotations

import json
from pathlib import Path

from game.constants import DEFAULT_DIFFICULTY

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"
VALID_DIFFICULTIES = {"easy", "normal", "hard", "expert"}
DEFAULT_SETTINGS = {
    "difficulty": DEFAULT_DIFFICULTY,
    "fullscreen": False,
    "show_fps": False,
}


def load_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()
    try:
        stored = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(stored, dict):
            settings.update({key: stored[key] for key in DEFAULT_SETTINGS if key in stored})
    except (OSError, json.JSONDecodeError):
        pass
    if settings["difficulty"] not in VALID_DIFFICULTIES:
        settings["difficulty"] = DEFAULT_DIFFICULTY
    settings["fullscreen"] = bool(settings["fullscreen"])
    settings["show_fps"] = bool(settings["show_fps"])
    return settings


def save_settings(settings: dict) -> None:
    clean = DEFAULT_SETTINGS.copy()
    clean.update({key: settings[key] for key in clean if key in settings})
    if clean["difficulty"] not in VALID_DIFFICULTIES:
        clean["difficulty"] = DEFAULT_DIFFICULTY
    try:
        SETTINGS_PATH.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        # The game remains playable if the directory is read-only.
        pass
