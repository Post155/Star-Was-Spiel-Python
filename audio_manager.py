"""Centralized Pygame audio subsystem for music and sound effects."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import pygame

try:
    from game.settings import DEFAULT_SETTINGS, load_settings, save_settings
except ImportError:
    DEFAULT_SETTINGS = {}
    load_settings = lambda: {}  # type: ignore
    save_settings = lambda settings: None  # type: ignore

LOGGER = logging.getLogger("audio")

MUSIC_FADE_IN_MS = 1500
MUSIC_FADE_OUT_MS = 1500
COMBAT_ENEMY_THRESHOLD = 5


class AudioManager:
    """Manage mixer initialization, music, effects, fading and persisted settings."""

    def __init__(self, asset_root: Optional[Path] = None, settings: Optional[Mapping[str, Any]] = None) -> None:
        self.asset_root = asset_root or (Path(__file__).resolve().parent / "assets" / "audio")
        self.music_dir = self.asset_root / "music"
        self.sfx_dir = self.asset_root / "sfx"
        self.settings: Dict[str, Any] = dict(load_settings() if settings is None else settings)
        self.enabled = True
        self.initialized = False
        self.current_music: Optional[str] = None
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._missing_files: set[Path] = set()
        self._initialize_mixer()
        self.apply_settings(self.settings)

    def _initialize_mixer(self) -> None:
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            pygame.mixer.set_num_channels(max(pygame.mixer.get_num_channels(), 32))
            self.initialized = True
        except (pygame.error, AttributeError) as exc:
            self.enabled = False
            LOGGER.error("Audio disabled: mixer initialization failed: %s", exc)

    def _warn_missing(self, path: Path) -> None:
        if path not in self._missing_files:
            LOGGER.warning("Audio disabled for missing or unavailable file: %s", path)
            self._missing_files.add(path)

    def apply_settings(self, settings: Mapping[str, Any]) -> None:
        """Apply and optionally persist a complete settings mapping."""
        self.settings.update(settings)
        self.settings["master_volume"] = self._clamp(self.settings.get("master_volume", 0.8))
        self.settings["music_volume"] = self._clamp(self.settings.get("music_volume", 0.6))
        self.settings["sfx_volume"] = self._clamp(self.settings.get("sfx_volume", 0.9))
        self.settings["menu_volume"] = self._clamp(self.settings.get("menu_volume", 0.7))
        self.settings["muted"] = bool(self.settings.get("muted", False))
        self.settings["dynamic_music"] = bool(self.settings.get("dynamic_music", True))
        if not self.initialized:
            self.enabled = False
        self._apply_music_volume()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            LOGGER.warning("Invalid audio volume; using 0.0")
            return 0.0

    def save_settings(self) -> None:
        save_settings(self.settings)

    def reset_to_defaults(self) -> None:
        defaults = dict(DEFAULT_SETTINGS)
        for key in ("difficulty", "fullscreen", "show_fps"):
            defaults[key] = self.settings.get(key, DEFAULT_SETTINGS.get(key))
        self.apply_settings(defaults)
        self.save_settings()

    def set_volume(self, category: str, volume: float) -> None:
        if category not in {"master_volume", "music_volume", "sfx_volume", "menu_volume"}:
            LOGGER.warning("Unknown volume category: %s", category)
            return
        self.settings[category] = self._clamp(volume)
        self._apply_music_volume()
        self.save_settings()

    def set_muted(self, muted: bool) -> None:
        self.settings["muted"] = bool(muted)
        self._apply_music_volume()
        self.save_settings()

    def set_dynamic_music(self, enabled: bool) -> None:
        self.settings["dynamic_music"] = bool(enabled)
        self.save_settings()

    def _master_factor(self) -> float:
        return 0.0 if self.settings.get("muted", False) else self.settings["master_volume"]

    def _apply_music_volume(self) -> None:
        if not self.initialized:
            return
        try:
            pygame.mixer.music.set_volume(self._master_factor() * self.settings["music_volume"])
        except pygame.error as exc:
            LOGGER.error("Unable to set music volume: %s", exc)

    def play_music(self, track: str, fade_in_ms: int = MUSIC_FADE_IN_MS) -> bool:
        """Cross-fade to a named track (menu.ogg, gameplay.ogg, etc.)."""
        if not self.enabled or not self.initialized or self.settings.get("muted", False):
            return False
        if self.current_music == track:
            return True
        path = self.music_dir / track
        if not path.is_file():
            self._warn_missing(path)
            return False
        try:
            pygame.mixer.music.fadeout(MUSIC_FADE_OUT_MS)
            pygame.mixer.music.load(str(path))
            self._apply_music_volume()
            pygame.mixer.music.play(loops=-1, fade_ms=max(0, fade_in_ms))
            self.current_music = track
            return True
        except pygame.error as exc:
            LOGGER.error("Unable to decode or play music %s: %s", path, exc)
            self.current_music = None
            return False

    def stop_music(self, fade_out_ms: int = MUSIC_FADE_OUT_MS) -> None:
        if not self.initialized:
            return
        try:
            if fade_out_ms > 0:
                pygame.mixer.music.fadeout(fade_out_ms)
            else:
                pygame.mixer.music.stop()
            self.current_music = None
        except pygame.error as exc:
            LOGGER.error("Unable to stop music: %s", exc)

    def pause_music(self) -> None:
        if not self.initialized:
            return
        try:
            pygame.mixer.music.pause()
        except pygame.error as exc:
            LOGGER.error("Unable to pause music: %s", exc)

    def resume_music(self) -> None:
        if not self.initialized:
            return
        try:
            pygame.mixer.music.unpause()
        except pygame.error as exc:
            LOGGER.error("Unable to resume music: %s", exc)

    def play_sfx(self, name: str, category: str = "sfx") -> bool:
        """Play a short sound effect in a free mixer channel."""
        if not self.enabled or not self.initialized or self.settings.get("muted", False):
            return False
        filename = {"laser": "laser.wav", "explosion": "explosion.wav", "damage": "damage.wav",
                    "hit": "damage.wav", "button": "button.wav", "powerup": "powerup.wav",
                    "warning": "warning.wav"}.get(name, f"{name}.wav")
        path = self.sfx_dir / filename
        sound = self._sounds.get(name)
        if sound is None:
            if not path.is_file():
                self._warn_missing(path)
                return False
            try:
                sound = pygame.mixer.Sound(str(path))
                self._sounds[name] = sound
            except pygame.error as exc:
                LOGGER.error("Unable to decode sound effect %s: %s", path, exc)
                return False
        volume_key = "menu_volume" if category == "menu" else "sfx_volume"
        volume = self._master_factor() * self.settings[volume_key]
        try:
            channel = pygame.mixer.find_channel(True)
            if channel is None:
                LOGGER.warning("No free mixer channel available for %s", name)
                return False
            channel.set_volume(volume)
            channel.play(sound)
            return True
        except pygame.error as exc:
            LOGGER.error("Unable to play sound effect %s: %s", name, exc)
            return False

    def set_game_state(self, *, state: Optional[str] = None, enemy_count: int = 0,
                       boss_active: bool = False, wave: int = 0, player_lives: int = 0,
                       mission_status: Optional[str] = None, phase: Optional[str] = None) -> None:
        """Event-based adaptive music selection; gameplay logic stays out of the manager's callers."""
        if not self.settings.get("dynamic_music", True):
            if state:
                self.play_music(f"{state}.ogg")
            return
        normalized = (mission_status or state or phase or "").lower()
        if normalized in {"victory", "win", "won"}:
            track = "victory.ogg"
        elif normalized in {"game_over", "defeat", "lost", "dead"}:
            track = "game_over.ogg"
        elif normalized == "pause" or phase == "pause":
            track = "pause.ogg"
        elif boss_active:
            track = "boss.ogg"
        elif enemy_count >= COMBAT_ENEMY_THRESHOLD or wave > 0:
            track = "combat.ogg"
        elif state == "lobby":
            track = "lobby.ogg"
        elif state in {"menu", "main_menu"}:
            track = "menu.ogg"
        elif state:
            track = f"{state}.ogg"
        else:
            track = "gameplay.ogg"
        self.play_music(track)


_audio_manager: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """Return the process-wide AudioManager singleton."""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
