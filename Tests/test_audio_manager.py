"""Unit tests for the centralized Pygame audio manager."""
import json

import pytest

from audio_manager import AudioManager
from game.settings import DEFAULT_SETTINGS


@pytest.fixture
def manager(tmp_path, monkeypatch):
    monkeypatch.setattr("pygame.mixer.get_init", lambda: (44100, -16, 2))
    monkeypatch.setattr("pygame.mixer.set_num_channels", lambda count: None)
    monkeypatch.setattr("pygame.mixer.get_num_channels", lambda: 32)
    monkeypatch.setattr("pygame.mixer.music.set_volume", lambda volume: None)
    monkeypatch.setattr("pygame.mixer.music.fadeout", lambda ms: None)
    monkeypatch.setattr("pygame.mixer.music.load", lambda path: None)
    monkeypatch.setattr("pygame.mixer.music.play", lambda **kwargs: None)
    monkeypatch.setattr("pygame.mixer.music.stop", lambda: None)
    monkeypatch.setattr("pygame.mixer.music.pause", lambda: None)
    monkeypatch.setattr("pygame.mixer.music.unpause", lambda: None)
    return AudioManager(asset_root=tmp_path / "audio", settings=dict(DEFAULT_SETTINGS))


def test_volume_is_clamped(manager):
    manager.set_volume("master_volume", 1.8)
    assert manager.settings["master_volume"] == 1.0
    manager.set_volume("sfx_volume", -0.2)
    assert manager.settings["sfx_volume"] == 0.0


def test_missing_music_is_handled(manager):
    assert manager.play_music("missing.ogg") is False


def test_music_switch_calls_fade_and_load(manager, tmp_path, monkeypatch):
    music_dir = tmp_path / "audio" / "music"
    music_dir.mkdir(parents=True)
    track = music_dir / "gameplay.ogg"
    track.write_bytes(b"fake")
    calls = []
    monkeypatch.setattr("pygame.mixer.music.load", lambda path: calls.append(("load", path)))
    monkeypatch.setattr("pygame.mixer.music.play", lambda **kwargs: calls.append(("play", kwargs)))

    assert manager.play_music("gameplay.ogg", fade_in_ms=1500) is True
    assert manager.current_music == "gameplay.ogg"
    assert calls[-1][1]["fade_ms"] == 1500


def test_dynamic_combat_and_boss_selection(manager, monkeypatch):
    calls = []
    monkeypatch.setattr(manager, "play_music", lambda track, fade_in_ms=1500: calls.append(track) or True)
    manager.set_game_state(state="gameplay", enemy_count=7)
    assert calls[-1] == "combat.ogg"
    manager.set_game_state(state="gameplay", boss_active=True)
    assert calls[-1] == "boss.ogg"


def test_mission_state_overrides_adaptive_music(manager, monkeypatch):
    calls = []
    monkeypatch.setattr(manager, "play_music", lambda track, fade_in_ms=1500: calls.append(track) or True)
    manager.set_game_state(state="gameplay", boss_active=True, mission_status="victory")
    assert calls[-1] == "victory.ogg"
    manager.set_game_state(state="gameplay", mission_status="game_over")
    assert calls[-1] == "game_over.ogg"


def test_missing_sfx_does_not_crash(manager):
    assert manager.play_sfx("laser") is False


def test_settings_save_and_load(tmp_path, monkeypatch):
    import game.settings as settings_module
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings_module, "SETTINGS_PATH", path)
    settings_module.save_settings({"master_volume": 0.45, "music_volume": 0.3, "muted": True})
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["master_volume"] == 0.45
    assert saved["muted"] is True
