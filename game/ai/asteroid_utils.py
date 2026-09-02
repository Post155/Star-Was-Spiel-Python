"""
asteroid_utils.py
Small helpers for using asteroids as cover and for filtering damaged asteroids.
"""
import numpy as np


def compute_cover_point(asteroid_pos, asteroid_radius, player_pos, offset=20.0):
    dir_from_player = np.array(asteroid_pos, dtype=float) - np.array(player_pos, dtype=float)
    norm = np.linalg.norm(dir_from_player)
    if norm < 1e-6:
        dir_from_player = np.array([1.0, 0.0])
    else:
        dir_from_player = dir_from_player / norm
    return np.array(asteroid_pos, dtype=float) + dir_from_player * (asteroid_radius + offset)


def is_asteroid_suitable(asteroid, min_integrity=0.3, avoid_recently_damaged=True):
    # asteroid expected to have attributes/keys: position, radius, integrity (0..1), last_hit_time (optional)
    integrity = getattr(asteroid, 'integrity', None)
    if integrity is None:
        integrity = asteroid.get('integrity', 1.0) if isinstance(asteroid, dict) else 1.0
    if integrity < min_integrity:
        return False
    if avoid_recently_damaged:
        last_hit = getattr(asteroid, 'last_hit_time', None) or (asteroid.get('last_hit_time') if isinstance(asteroid, dict) else None)
        if last_hit is not None:
            # if very recent, avoid
            return False
    return True