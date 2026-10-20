import json
from pathlib import Path

from game.settings import DEFAULT_SETTINGS, load_settings, save_settings


def test_load_settings_returns_defaults_for_missing_file(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr("game.settings.SETTINGS_PATH", settings_file)

    actual = load_settings()

    assert actual["difficulty"] == DEFAULT_SETTINGS["difficulty"]
    assert actual["fullscreen"] is False
    assert actual["show_fps"] is False


def test_save_settings_validates_and_persists(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr("game.settings.SETTINGS_PATH", settings_file)

    save_settings({"difficulty": "expert", "fullscreen": True, "show_fps": True, "unknown": 123})

    persisted = json.loads(settings_file.read_text(encoding="utf-8"))
    assert persisted["difficulty"] == "expert"
    assert persisted["fullscreen"] is True
    assert persisted["show_fps"] is True
    assert "unknown" not in persisted


def test_load_settings_rejects_invalid_difficulty(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr("game.settings.SETTINGS_PATH", settings_file)
    settings_file.write_text(json.dumps({"difficulty": "nightmare", "fullscreen": "yes"}), encoding="utf-8")

    actual = load_settings()

    assert actual["difficulty"] == DEFAULT_SETTINGS["difficulty"]
    assert actual["fullscreen"] is True
