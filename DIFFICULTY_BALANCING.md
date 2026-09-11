# Difficulty & Balancing

All important difficulty values are in `game/constants.py`.

## Difficulty presets

Change `DIFFICULTY_SETTINGS` to tune:
- `enemy_accuracy`
- `enemy_hp`
- `enemy_speed`
- `enemy_aggression`
- `enemy_max`
- `enemy_spawn`
- `asteroid_density`
- `asteroid_speed`
- `asteroid_size`

## Enemy unlocks

- `ENEMY_UNLOCK_STANDARD_POINTS = 1000`
- `ENEMY_UNLOCK_HEAVY_POINTS = 3000`
- `ENEMY_UNLOCK_ELITE_POINTS = 6000`

No enemy can spawn before 1000 points.

## Star-system scaling

`SYSTEM_DIFFICULTY_BONUS` controls the additional difficulty per system:
- system 1: 0%
- system 2: 15%
- system 3: 30%
- system 4: 50%

Later systems use the last configured value. Edit the tuple in `constants.py` if more individual stages are wanted.

The system bonus affects enemy HP/speed/accuracy/aggression and asteroid density/speed/size.
