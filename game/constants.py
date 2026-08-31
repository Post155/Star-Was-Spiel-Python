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
    "x_wing": "Pixelarts/x_wing.png",
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


# How often (frames) a new asteroid is spawned. Increase to spawn less often, decrease to spawn more often.
ASTEROID_SPAWN_INTERVAL = 60

# Default system switch thresholds
# LEVEL SETTINGS: change these values to adjust how quickly the game advances to the next sector.
# The actual level order is defined in game/background/systems.py.
SYSTEM_SWITCH_POINTS = 500
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
