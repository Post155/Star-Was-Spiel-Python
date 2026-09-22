WIDTH = 800
HEIGHT = 600
SCREEN_TITLE = "Star Wars"

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

ASSET_PATHS = {
    "window_icon": "Pixelarts/icon.ico",
    "tie_fighter": "Pixelarts/tie-fighter.png",
    "battle_droid": "Pixelarts/Battle_Droid.png",
    "x_wing": "Pixelarts/X_Wing.png",
    "millennium_falcon": "Pixelarts/millennium.png",
    "rebel_logo": "Pixelarts/Star-Wars-Rebel-Logo.png",
    "empire_logo": "Pixelarts/Galactic-Empire-Logo.png",
    "torpedo": "Pixelarts/Torpedo.png",
    "explosion": "Pixelarts/Explosion.png",
    "lightsabers": "Pixelarts/lichtschwerter.png",
    "asteroid_frames": [
        "Pixelarts/Astroids/frame_00.png",
        "Pixelarts/Astroids/frame_01.png",
        "Pixelarts/Astroids/frame_02.png",
        "Pixelarts/Astroids/frame_03.png",
        "Pixelarts/Astroids/frame_04.png",
        "Pixelarts/Astroids/frame_05.png",
        "Pixelarts/Astroids/frame_06.png",
        "Pixelarts/Astroids/frame_07.png",
        "Pixelarts/Astroids/frame_08.png",
        "Pixelarts/Astroids/frame_09.png",
        "Pixelarts/Astroids/frame_10.png",
        "Pixelarts/Astroids/frame_11.png",
    ],

    # Star system specific assets (optional - loader ignores missing files)
    "earth": "Pixelarts/Systems/earth.png",
    "coruscant": "Pixelarts/Systems/coruscant.png",
    "satellites": "Pixelarts/Systems/satellites.png",
    "tatooine_planet": "Pixelarts/Systems/tatooine_planet.png",
    "sun_1": "Pixelarts/Systems/sun_1.png",
    "sun_2": "Pixelarts/Systems/sun_2.png",
    "gelber_nebel": "Pixelarts/Systems/gelber_nebel.png",
    "hoth_planet": "Pixelarts/Systems/hoth_planet.png",
    "blue_nebula": "Pixelarts/Systems/blue_nebula.png",
    "endor": "Pixelarts/Systems/endor.png",
    "forest_moon": "Pixelarts/Systems/forest_moon.png",
    "death_star": "Pixelarts/Systems/death_star.png",
    "imperial_station": "Pixelarts/Systems/imperial_station.png",
    "star_destroyer": "Pixelarts/Systems/star_destroyer.png",
    "nebula_red": "Pixelarts/Systems/nebula_red.png",
    "nebula_blue": "Pixelarts/Systems/nebula_blue.png",
    "nebula_purple": "Pixelarts/Systems/nebula_purple.png",
    "xwing_squadron": "Pixelarts/Systems/xwing_squadron.png",
    "tie_fighter": "Pixelarts/tie-fighter.png",
    "battle_explosion": "Pixelarts/Systems/battle_explosion.png",
    "hyperraum": "Pixelarts/Hyperraum.png",
}

# Hyperraum (hyperspace) full cinematic sequence duration in milliseconds
# Default set to 14000 (14 seconds) to allow multi-phase cinematic sequences
# Can be adjusted between ~12000 and ~18000 for shorter/longer experiences.
HYPERSPACE_DURATION_MS = 14000

# Duration of the Galaxy Map (Phase 4) in milliseconds when using map-only transitions
GALAXY_MAP_DURATION_MS = 5000


# How often (frames) a new asteroid is spawned. Increase to spawn less often, decrease to spawn more often.
ASTEROID_SPAWN_INTERVAL = 60

# Default system switch thresholds
# LEVEL SETTINGS: change these values to adjust how quickly the game advances to the next sector.
# The actual level order is defined in game/background/systems.py.
SYSTEM_SWITCH_POINTS = 2000
SYSTEM_SWITCH_TIME_MS = 30000  # 2 minutes in milliseconds

# Player and ship speeds (change these to adjust how fast ships move)
PLAYER_BASE_SPEED = 10  # default base speed for generic player
SHIP_SPEED_XWING = 12
SHIP_SPEED_MILLENNIUM = 14
SHIP_SPEED_TIEFIGHTER = 11
SHIP_SPEED_BATTLEDROID = 12

# Scales for ship sprites (change these to resize the ships)
SHIP_SCALE_XWING = 0.20
SHIP_SCALE_MILLENNIUM = 0.75
SHIP_SCALE_TIEFIGHTER = 0.30
SHIP_SCALE_BATTLEDROID = 0.12

# Asteroid speed range (min, max)
ASTEROID_SPEED_RANGE = (2, 8)

# ============================================================================
# DIFFICULTY / BALANCING
# ============================================================================
# All gameplay balancing values are centralized here.
# Change these values to fine-tune the game without editing the game loop.
#
# Difficulty:
#   EASY     = Einfach
#   NORMAL   = Normal
#   HARD     = Schwer
#   EXPERT   = Experte

DIFFICULTY_SETTINGS = {
    "easy": {
        "name": "Einfach",
        "enemy_accuracy": 0.72,
        "enemy_hp": 0.80,
        "enemy_speed": 0.82,
        "enemy_aggression": 0.70,
        "enemy_max": 0.65,
        "enemy_spawn": 1.25,
        "asteroid_density": 0.78,
        "asteroid_speed": 0.82,
        "asteroid_size": 0.90,
    },
    "normal": {
        "name": "Normal",
        "enemy_accuracy": 0.90,
        "enemy_hp": 1.00,
        "enemy_speed": 0.95,
        "enemy_aggression": 0.88,
        "enemy_max": 0.82,
        "enemy_spawn": 1.10,
        "asteroid_density": 0.90,
        "asteroid_speed": 0.92,
        "asteroid_size": 0.95,
    },
    "hard": {
        "name": "Schwer",
        "enemy_accuracy": 1.00,
        "enemy_hp": 1.12,
        "enemy_speed": 1.05,
        "enemy_aggression": 1.05,
        "enemy_max": 1.00,
        "enemy_spawn": 0.92,
        "asteroid_density": 1.05,
        "asteroid_speed": 1.05,
        "asteroid_size": 1.00,
    },
    "expert": {
        "name": "Experte",
        "enemy_accuracy": 1.08,
        "enemy_hp": 1.25,
        "enemy_speed": 1.14,
        "enemy_aggression": 1.20,
        "enemy_max": 1.15,
        "enemy_spawn": 0.80,
        "asteroid_density": 1.18,
        "asteroid_speed": 1.15,
        "asteroid_size": 1.08,
    },
}

DEFAULT_DIFFICULTY = "normal"

# Enemy progression is score based. Before the first threshold the player
# fights asteroids only.
ENEMY_UNLOCK_STANDARD_POINTS = 1000
ENEMY_UNLOCK_HEAVY_POINTS = 3000
ENEMY_UNLOCK_ELITE_POINTS = 6000

# Difficulty added by entering later star systems.
# System 1 = 0%, System 2 = +15%, System 3 = +30%, System 4 = +50%.
# Later systems continue with the last value unless explicitly configured.
SYSTEM_DIFFICULTY_BONUS = (0.00, 0.15, 0.30, 0.50)

# Additional gradual scaling inside a system. This prevents a sudden jump
# immediately after a system transition.
SYSTEM_PROGRESS_MAX_BONUS = 0.20

# Warning display before a new enemy class can spawn.
ENEMY_WARNING_DURATION_MS = 2600

# Asteroid tuning. These are deliberately separate so they can be adjusted.
ASTEROID_BASE_SPAWN_INTERVAL = ASTEROID_SPAWN_INTERVAL
ASTEROID_MIN_SPAWN_INTERVAL = 22
ASTEROID_SIZE_RANGE = (0.25, 1.00)
