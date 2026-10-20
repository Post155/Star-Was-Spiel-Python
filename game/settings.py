"""Persistent user settings for the Star Wars game."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from game.config import DEFAULT_DIFFICULTY, VALID_DIFFICULTIES

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"
DEFAULT_SETTINGS = {
    "difficulty": DEFAULT_DIFFICULTY,
    "fullscreen": False,
    "show_fps": False,
}


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off", ""}:
            return False
    return default


def _clean_settings(raw: dict[str, Any] | None) -> dict[str, Any]:
    cleaned = DEFAULT_SETTINGS.copy()
    if not isinstance(raw, dict):
        return cleaned
    for key in DEFAULT_SETTINGS:
        if key in raw:
            cleaned[key] = raw[key]

    cleaned["difficulty"] = str(cleaned.get("difficulty", DEFAULT_DIFFICULTY) or DEFAULT_DIFFICULTY).strip().lower()
    if cleaned["difficulty"] not in VALID_DIFFICULTIES:
        cleaned["difficulty"] = DEFAULT_DIFFICULTY
    cleaned["fullscreen"] = _as_bool(cleaned.get("fullscreen"), False)
    cleaned["show_fps"] = _as_bool(cleaned.get("show_fps"), False)
    return cleaned


def load_settings() -> dict[str, Any]:
    settings = DEFAULT_SETTINGS.copy()
    try:
        loaded = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _clean_settings(settings)
    return _clean_settings(loaded)


def save_settings(settings: dict[str, Any]) -> None:
    clean = _clean_settings(settings)
    try:
        SETTINGS_PATH.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        # The game remains playable if the directory is read-only.
        pass
