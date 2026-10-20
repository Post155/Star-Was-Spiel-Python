from game.constants import DEFAULT_DIFFICULTY, DIFFICULTY_SETTINGS


def test_difficulty_profiles_are_defined():
    assert set(DIFFICULTY_SETTINGS) == {"easy", "normal", "hard", "expert"}
    assert DEFAULT_DIFFICULTY in DIFFICULTY_SETTINGS

    for difficulty, settings in DIFFICULTY_SETTINGS.items():
        assert "name" in settings
        assert settings["enemy_accuracy"] > 0
        assert settings["enemy_hp"] > 0
        assert settings["enemy_speed"] > 0
