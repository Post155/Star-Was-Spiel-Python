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
}

# How often (frames) a new asteroid is spawned. Increase to spawn less often, decrease to spawn more often.
ASTEROID_SPAWN_INTERVAL = 60

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
