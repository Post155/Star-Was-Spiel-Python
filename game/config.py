"""Centralized project configuration and path helpers.

This module provides a single place for project-root and asset-path resolution so
that the game keeps working regardless of the current working directory.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAME_ROOT = PROJECT_ROOT / "game"
ASSETS_ROOT = PROJECT_ROOT / "assets"
PIXELARTS_ROOT = PROJECT_ROOT / "Pixelarts"

VALID_DIFFICULTIES = ("easy", "normal", "hard", "expert")
DEFAULT_DIFFICULTY = "normal"


def resolve_path(*parts: str | Path) -> Path:
    """Resolve a path relative to the project root."""
    return (PROJECT_ROOT.joinpath(*[str(part) for part in parts])).resolve()


def resolve_asset_path(path: str | Path | None) -> str:
    """Return a stable absolute path for an asset or project resource."""
    if not path:
        return ""

    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)

    search_roots: Iterable[Path] = (
        PROJECT_ROOT,
        GAME_ROOT,
        ASSETS_ROOT,
        PIXELARTS_ROOT,
        PROJECT_ROOT / "assets",
        PROJECT_ROOT / "Pixelarts",
    )
    for root in search_roots:
        absolute = (root / candidate).resolve()
        if absolute.exists():
            return str(absolute)

    return str((PROJECT_ROOT / candidate).resolve())


def normalize_difficulty(value: object, default: str = DEFAULT_DIFFICULTY) -> str:
    """Validate and normalize the selected difficulty."""
    as_text = str(value or default).strip().lower()
    return as_text if as_text in VALID_DIFFICULTIES else default
