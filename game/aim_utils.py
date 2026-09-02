"""
aim_utils.py
Utilities for predictive aiming (leading) using numpy arrays as used in game.enemy_ai.
"""
import numpy as np


def leading_position(shooter_pos: np.ndarray,
                     target_pos: np.ndarray,
                     target_vel: np.ndarray,
                     projectile_speed: float,
                     max_iter: int = 5) -> np.ndarray:
    """
    Compute an intercept point by iteratively solving for time t where
    projectile_speed * t = ||(target_pos + target_vel * t) - shooter_pos||
    Returns the estimated future target position (numpy array).
    """
    shooter_pos = np.array(shooter_pos, dtype=np.float64)
    target_pos = np.array(target_pos, dtype=np.float64)
    target_vel = np.array(target_vel, dtype=np.float64)

    rel = target_pos - shooter_pos
    dist = np.linalg.norm(rel)
    if dist < 1e-6:
        return target_pos.copy()

    # initial guess: time = distance / speed
    t = dist / max(1e-6, projectile_speed)
    for _ in range(max_iter):
        future_pos = target_pos + target_vel * t
        d = np.linalg.norm(future_pos - shooter_pos)
        if d < 1e-6:
            break
        new_t = d / max(1e-6, projectile_speed)
        if abs(new_t - t) < 1e-3:
            t = new_t
            break
        t = 0.5 * (t + new_t)
    return target_pos + target_vel * t


def compute_shot_direction(shooter_pos: np.ndarray,
                           target_pos: np.ndarray,
                           target_vel: np.ndarray,
                           projectile_speed: float):
    lead = leading_position(shooter_pos, target_pos, target_vel, projectile_speed)
    dir_vec = lead - np.array(shooter_pos, dtype=np.float64)
    norm = np.linalg.norm(dir_vec)
    if norm < 1e-9:
        return np.array([0.0, 0.0], dtype=np.float64)
    return dir_vec / norm
