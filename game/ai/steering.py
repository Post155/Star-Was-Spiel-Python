"""
steering.py
Steering behavior implementations using numpy arrays.
"""
import numpy as np


def seek(agent_pos, target_pos, max_speed):
    desired = np.array(target_pos, dtype=np.float64) - np.array(agent_pos, dtype=np.float64)
    dist = np.linalg.norm(desired)
    if dist < 1e-6:
        return np.zeros(2, dtype=np.float64)
    return (desired / dist) * max_speed


def arrive(agent_pos, target_pos, max_speed, slowing_radius):
    to_target = np.array(target_pos, dtype=np.float64) - np.array(agent_pos, dtype=np.float64)
    dist = np.linalg.norm(to_target)
    if dist < 1e-6:
        return np.zeros(2, dtype=np.float64)
    if dist < slowing_radius:
        desired_speed = max_speed * (dist / slowing_radius)
    else:
        desired_speed = max_speed
    return (to_target / dist) * desired_speed


def pursuit(agent, target_agent, max_speed):
    rel_pos = np.array(target_agent.position) - np.array(agent.position)
    rel_speed = max_speed + np.linalg.norm(target_agent.velocity)
    if rel_speed <= 1e-6:
        return seek(agent.position, target_agent.position, max_speed)
    look_ahead = np.linalg.norm(rel_pos) / rel_speed
    future_pos = np.array(target_agent.position) + np.array(target_agent.velocity) * look_ahead
    return seek(agent.position, future_pos, max_speed)


def evade(agent, pursuer, max_speed):
    rel_pos = np.array(pursuer.position) - np.array(agent.position)
    rel_speed = np.linalg.norm(agent.velocity) + 1e-6
    look_ahead = np.linalg.norm(rel_pos) / rel_speed
    future_pos = np.array(pursuer.position) + np.array(pursuer.velocity) * look_ahead
    desired = np.array(agent.position) - future_pos
    norm = np.linalg.norm(desired)
    if norm < 1e-6:
        return np.zeros(2, dtype=np.float64)
    return (desired / norm) * max_speed


def separation(agent, neighbors, desired_separation, max_force):
    steer = np.zeros(2, dtype=np.float64)
    count = 0
    for n in neighbors:
        diff = np.array(agent.position) - np.array(n.position)
        d = np.linalg.norm(diff)
        if 0 < d < desired_separation:
            steer += (diff / (d + 1e-6))
            count += 1
    if count > 0:
        steer /= float(count)
        norm = np.linalg.norm(steer)
        if norm > 1e-6:
            steer = (steer / norm) * max_force
    return steer


def cohesion(agent, neighbors, max_speed):
    center = np.zeros(2, dtype=np.float64)
    count = 0
    for n in neighbors:
        center += np.array(n.position)
        count += 1
    if count == 0:
        return np.zeros(2, dtype=np.float64)
    center /= float(count)
    return seek(agent.position, center, max_speed)


def obstacle_avoidance(agent, obstacles, avoid_distance, max_force):
    steer = np.zeros(2, dtype=np.float64)
    v = np.array(agent.velocity, dtype=np.float64)
    vnorm = np.linalg.norm(v)
    if vnorm < 1e-6:
        vdir = np.array([1.0, 0.0])
    else:
        vdir = v / vnorm
    for obs in obstacles:
        to_obs = np.array(obs.position, dtype=np.float64) - np.array(agent.position, dtype=np.float64)
        proj = np.dot(vdir, to_obs)
        if 0 < proj < avoid_distance:
            closest = np.array(agent.position) + vdir * proj
            diff = closest - np.array(obs.position, dtype=np.float64)
            d = np.linalg.norm(diff)
            if d < 1e-6:
                perp = np.array([-vdir[1], vdir[0]])
                steer += perp * max_force
            else:
                steer += (diff / d) * max_force
    return steer