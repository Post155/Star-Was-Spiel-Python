"""Persistent user settings for the Star Wars game."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from game.config import DEFAULT_DIFFICULTY, VALID_DIFFICULTIES


def _default_settings_directory() -> Path:
    """Return a writable platform-specific application settings directory."""
    try:
        from platformdirs import user_data_dir
        return Path(user_data_dir("StarWarsGalacticAssault", "Post155"))
    except ImportError:
        if sys.platform.startswith("win"):
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        return base / "StarWarsGalacticAssault"


SETTINGS_PATH = _default_settings_directory() / "settings.json"
_LEGACY_SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"
DEFAULT_SETTINGS = {
    "difficulty": DEFAULT_DIFFICULTY,
    "fullscreen": False,
    "show_fps": False,
    "master_volume": 0.8,
    "music_volume": 0.6,
    "sfx_volume": 0.9,
    "menu_volume": 0.7,
    "dynamic_music": True,
    "muted": False,
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


def _clamped_volume(value: Any, default: float) -> float:
    try:
        volume = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, volume))


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
    cleaned["dynamic_music"] = _as_bool(cleaned.get("dynamic_music"), True)
    cleaned["muted"] = _as_bool(cleaned.get("muted"), False)
    for key in ("master_volume", "music_volume", "sfx_volume", "menu_volume"):
        cleaned[key] = _clamped_volume(cleaned.get(key), DEFAULT_SETTINGS[key])
    return cleaned


def load_settings() -> dict[str, Any]:
    try:
        loaded = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Migration: preserve settings previously stored in the project folder.
        try:
            loaded = json.loads(_LEGACY_SETTINGS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            loaded = DEFAULT_SETTINGS.copy()
    return _clean_settings(loaded)


def save_settings(settings: dict[str, Any]) -> None:
    clean = _clean_settings(settings)
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        # The game remains playable if the directory is read-only.
        pass
