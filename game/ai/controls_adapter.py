"""
controls_adapter.py
Maps steering desired velocity vectors to ship control commands (turn, thrust) using a simple proportional controller.
This adapter uses the EnemyShip attributes: position, velocity, heading (degrees), stats.max_speed
and expects the owner to expose methods or attributes to set controls (here it will directly mutate velocity/heading
via simple physics updates to remain compatible with existing EnemyShip._execute_action patterns).
"""
import math
import numpy as np


def apply_steering_to_controls(owner, desired_vel: np.ndarray, dt: float):
    """
    owner: the EnemyShip instance
    desired_vel: numpy array [vx, vy] world-space desired velocity (not necessarily clamped)
    dt: delta time

    This function modifies owner.velocity and owner.heading (degrees) using a simple mapping.
    It does not rely on any external input interface so it's non-breaking.
    """
    if desired_vel is None:
        return
    # desired heading
    dv = np.array(desired_vel, dtype=float)
    if np.linalg.norm(dv) < 1e-6:
        # no steering requested; lightly damp velocity
        owner.velocity *= 0.98
        return
    desired_angle = math.degrees(math.atan2(dv[1], dv[0]))
    # normalize angles to [-180,180]
    cur = owner.heading
    diff = (desired_angle - cur + 180.0) % 360.0 - 180.0
    # proportional turn: scale by turn_rate and dt, clamp
    max_turn = owner.stats.turn_rate * dt
    turn = max(-max_turn, min(max_turn, diff))
    owner.heading = (owner.heading + turn) % 360.0
    # desired speed magnitude
    desired_speed = min(np.linalg.norm(dv), owner.stats.max_speed)
    # forward vector
    rad = math.radians(owner.heading)
    forward = np.array([math.cos(rad), math.sin(rad)])
    # compute simple throttle to approach desired_speed
    current_forward_speed = np.dot(owner.velocity, forward)
    speed_error = desired_speed - current_forward_speed
    # apply acceleration proportional to speed_error
    accel = (speed_error / max(1.0, owner.stats.max_speed)) * owner.stats.max_speed * 0.8
    owner.velocity += forward * accel * dt
    # clamp velocity magnitude
    vmag = np.linalg.norm(owner.velocity)
    if vmag > owner.stats.max_speed:
        owner.velocity = (owner.velocity / vmag) * owner.stats.max_speed
