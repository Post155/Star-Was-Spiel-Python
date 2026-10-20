from game.network import MAX_NAME_LENGTH, LAN_PORT, PROTOCOL_VERSION, _safe_float, _safe_int, _safe_name


def test_safe_helpers_enforce_bounds():
    assert _safe_name("   ") == "Spieler"
    assert _safe_name("x" * 100) == ("x" * MAX_NAME_LENGTH)
    assert _safe_int("7") == 7
    assert _safe_int("-10", default=5, minimum=0) == 0
    assert _safe_float("2.5") == 2.5
    assert _safe_float("invalid", default=1.25) == 1.25


def test_protocol_metadata_is_consistent():
    assert isinstance(LAN_PORT, int)
    assert PROTOCOL_VERSION >= 1
    assert MAX_NAME_LENGTH > 0
