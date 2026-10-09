# File-by-file migration

The excerpts below come from the uploaded Python project. They are included to keep the port traceable. The corresponding Unity implementation is listed next to each file.

## `StarWarsGame.py`

**Unity target:** `Core/GameBootstrap.cs + Core/GameSession.cs + UI/* + Multiplayer/*`

**Original Python excerpt:**

```python
import sys

import pygame

from game.assets import load_assets, set_window_icon
from game.background import BackgroundManager
from game.constants import (
    ASTEROID_SPAWN_INTERVAL,
    BLACK,
    HEIGHT,
    SCREEN_TITLE,
    WIDTH,
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
    ASTEROID_MIN_SPAWN_INTERVAL,
)
from game.enemies import EnemyManager
from game.entities.asteroid import Asteroid
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/StarWarsGame.py`

**Unity target:** `Core/GameSession.cs + UI/* + Multiplayer/*`

**Original Python excerpt:**

```python
import sys

import pygame

from game.assets import load_assets, set_window_icon
from game.background import BackgroundManager
from game.constants import (
    ASTEROID_SPAWN_INTERVAL,
    BLACK,
    HEIGHT,
    SCREEN_TITLE,
    WIDTH,
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
    ASTEROID_MIN_SPAWN_INTERVAL,
)
from game.enemies import EnemyManager
from game.entities.asteroid import Asteroid
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/__init__.py`

**Unity target:** `No direct C# equivalent`

**Original Python excerpt:**

```python
# game package
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/assets.py`

**Unity target:** `Core/AssetLibrary.cs`

**Original Python excerpt:**

```python
import os

import pygame

from game.constants import ASSET_PATHS


PLANET_NAME_ALIASES = {
    'earth': 'earth',
    'coruscant': 'corusant',
    'satellites': 'saturn',
    'tatooine_planet': 'tatooine',
    'hoth_planet': 'hoth',
    'endor': 'endor',
    'forest_moon': 'endor',
    'death_star': 'todesstern',
    'imperial_station': 'imperial_station',
    'star_destroyer': 'sternzerstoerer',
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/__init__.py`

**Unity target:** `No direct C# equivalent; namespace/file structure replaces it`

**Original Python excerpt:**

```python
from .manager import BackgroundManager
from .systems import StarSystem

__all__ = ["BackgroundManager", "StarSystem"]

SYSTEM_ENTRY_DELAY_MS = 5000   # 5 Sekunden
SYSTEM_EXIT_DELAY_MS  = 5000    # 5 Sekunden vor Wechsel

PLANET_FORCE_SINGLE_PASS = True
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/manager.py`

**Unity target:** `Gameplay/Background/BackgroundManager.cs`

**Original Python excerpt:**

```python
import random
from typing import List, Optional

import pygame
import math

from game.constants import HEIGHT as DEFAULT_HEIGHT
from game.constants import WIDTH as DEFAULT_WIDTH
from game.constants import SYSTEM_SWITCH_POINTS, SYSTEM_SWITCH_TIME_MS
from game.constants import HYPERSPACE_DURATION_MS
from game.constants import DIFFICULTY_SETTINGS, DEFAULT_DIFFICULTY, SYSTEM_DIFFICULTY_BONUS, SYSTEM_PROGRESS_MAX_BONUS

from .objects import ForegroundObject
from .planet_manager import PlanetManager
from .starfield import StarField
from .system_manager import SystemManager
from .transition_manager import TransitionManager

# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/objects.py`

**Unity target:** `Gameplay/Background/StarfieldController.cs + PlanetController.cs`

**Original Python excerpt:**

```python
import random

import pygame


class Star:
    def __init__(self, width, height, layer=1, tint=None):
        self.width = width
        self.height = height
        self.layer = layer
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

        # size and speed influenced by layer for parallax
        if layer == 1:
            self.size = random.choice([1, 1, 1, 1])
            self.base_speed = 0.12
            self.brightness_min = 110
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/planet_manager.py`

**Unity target:** `Gameplay/Background/PlanetController.cs + BackgroundManager.cs`

**Original Python excerpt:**

```python
"""PlanetManager: spawn, update and draw planets for the current system.

Responsibility:
- Ensure one planet per system (configurable)
- Spawn planets when allowed and respecting entry/exit delays
- Update planetary motion and removal
- Expose simple interface for coordinator BackgroundManager
"""
from typing import List, Optional, Tuple
import random
import pygame
from .objects import Planet


class PlanetManager:
    def __init__(self, width: int, height: int, assets: Optional[dict] = None) -> None:
        self.width = width
        self.height = height
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/starfield.py`

**Unity target:** `Gameplay/Background/StarfieldController.cs`

**Original Python excerpt:**

```python
"""StarField subsystem: manage star layers (spawn, update, render).

Responsibility:
- Initialize star layers according to density/tint
- Update star positions
- Draw stars
"""
from typing import List, Optional
import pygame
from .objects import Star


class StarField:
    def __init__(self, width: int, height: int, density: float = 1.0, tint: Optional[tuple] = None) -> None:
        self.width = width
        self.height = height
        self.density = max(0.1, float(density))
        self.tint = tint
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/system_manager.py`

**Unity target:** `Gameplay/Background/StarSystemManager.cs`

**Original Python excerpt:**

```python
"""SystemManager: manage star system order, selection and difficulty.

Responsibility:
- Build systems from configuration
- Provide current system and ordering operations
- Encapsulate visited tracking and next-system selection
"""
from typing import List, Optional, Set
import random
from .systems import StarSystem, build_systems


class SystemManager:
    def __init__(self, assets: Optional[dict] = None) -> None:
        self.assets = assets or {}
        self.systems: List[StarSystem] = build_systems(self.assets)

        if self.systems:
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/systems.py`

**Unity target:** `Data/StarSystemDefinition.cs + Core/RuntimeContent.cs`

**Original Python excerpt:**

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StarSystem:
    """Configuration holder for a star system/sector."""

    id_name: str
    display_lines: List[str]
    planet_keys: List[str] = field(default_factory=list)
    foreground_keys: List[str] = field(default_factory=list)
    star_tint: Optional[tuple] = None
    star_density: float = 1.0
    asteroid_speed_mul: float = 1.0
    nebula_keys: List[str] = field(default_factory=list)
    extra_flags: Dict[str, object] = field(default_factory=dict)
    difficulty: int = 1
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/background/transition_manager.py`

**Unity target:** `Gameplay/Background/BackgroundManager.cs`

**Original Python excerpt:**

```python
"""TransitionManager: handle system transitions (galaxy map / hyperdrive animations).

Responsibility:
- Track transition timing and phases
- Render the map-only transition sequence used by the game
- Provide a simple API to start a transition and indicate completion
"""
from typing import List, Optional, Dict
import pygame
import math
import random

from .systems import StarSystem


class TransitionManager:
    def __init__(self, width: int, height: int, assets: Optional[dict] = None) -> None:
        self.width = width
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/constants.py`

**Unity target:** `Core/GameConstants.cs`

**Original Python excerpt:**

```python
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
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/__init__.py`

**Unity target:** `No direct C# equivalent; namespace/file structure replaces it`

**Original Python excerpt:**

```python
"""Public enemy AI API."""
from .base import EnemyBase
from .manager import EnemyManager, EnemyUpdateResult

__all__ = ["EnemyBase", "EnemyManager", "EnemyUpdateResult"]
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/ai.py`

**Unity target:** `Gameplay/EnemyBrain.cs`

**Original Python excerpt:**

```python
"""Decision-making component for AI enemies."""
from __future__ import annotations

import random


ROLE_OFFSETS = {
    "attacker": 0.0,
    "support": 0.18,
    "flanker_left": -0.26,
    "flanker_right": 0.26,
}

ROLE_Y = {
    "attacker": 0.34,
    "support": 0.18,
    "flanker_left": 0.27,
    "flanker_right": 0.27,
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/base.py`

**Unity target:** `Gameplay/EnemyController.cs`

**Original Python excerpt:**

```python
"""Base class for all AI-controlled enemy ships."""
from __future__ import annotations

import random
import pygame

from game.constants import normalize_ship_scale

from .ai import EnemyBrain
from .movement import EnemyMovement
from .weapons import EnemyWeaponSystem


class EnemyBase:
    """Composable enemy entity used by standard, fast, heavy and elite variants.

    Bosses can later subclass this class while reusing movement, weapons and
    collision handling, or replace individual components.
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/config.py`

**Unity target:** `Data/EnemyArchetype.cs + Core/RuntimeContent.cs`

**Original Python excerpt:**

```python
"""Enemy configuration and ship-opposition rules.

The data in this module deliberately contains no pygame logic. New variants,
bosses or faction rules can be added here without touching the main game loop.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from game.constants import (
    SHIP_SCALE_BATTLEDROID,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_XWING,
)


# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/manager.py`

**Unity target:** `Gameplay/EnemyManager.cs`

**Original Python excerpt:**

```python
"""Enemy spawning, balancing, unlock progression, collisions and lifecycle."""
from __future__ import annotations

import random
from dataclasses import dataclass, replace

from game.constants import (
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
    ENEMY_UNLOCK_STANDARD_POINTS,
    ENEMY_UNLOCK_HEAVY_POINTS,
    ENEMY_UNLOCK_ELITE_POINTS,
    ENEMY_WARNING_DURATION_MS,
    SYSTEM_DIFFICULTY_BONUS,
    SYSTEM_PROGRESS_MAX_BONUS,
)

from game.entities.explosion import Explosion
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/movement.py`

**Unity target:** `Gameplay/EnemyMovement.cs`

**Original Python excerpt:**

```python
"""Steering / movement component for enemies."""
from __future__ import annotations

import math


class EnemyMovement:
    """Applies acceleration-limited steering for natural enemy motion."""

    def __init__(self, owner):
        self.owner = owner

    @staticmethod
    def _approach(current, target, max_delta):
        if current < target:
            return min(current + max_delta, target)
        return max(current - max_delta, target)

# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/projectiles.py`

**Unity target:** `Gameplay/ProjectileController.cs`

**Original Python excerpt:**

```python
"""Projectiles fired by AI enemies."""
from __future__ import annotations

import math
import pygame


class EnemyProjectileBase:
    def __init__(self, x, y, target_x, target_y, speed, damage):
        self.x = float(x)
        self.y = float(y)
        self.damage = int(damage)
        dx = float(target_x) - self.x
        dy = float(target_y) - self.y
        length = max(1.0, math.hypot(dx, dy))
        self.vx = dx / length * speed
        self.vy = dy / length * speed
        self.alive = True
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/enemies/weapons.py`

**Unity target:** `Gameplay/EnemyWeaponSystem.cs`

**Original Python excerpt:**

```python
"""Enemy weapon component: bursts, aimed lasers and tactical torpedoes."""
from __future__ import annotations

import random

from .projectiles import EnemyLaser, EnemyTorpedo


class EnemyWeaponSystem:
    def __init__(self, owner, torpedo_image=None):
        self.owner = owner
        self.torpedo_image = torpedo_image
        self.laser_timer = random.uniform(0.35, 1.2)
        self.torpedo_timer = random.uniform(*owner.archetype.torpedo_cooldown)
        self.burst_remaining = 0
        self.burst_timer = 0.0

    def _aim_point(self, player, difficulty_scale):
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities/__init__.py`

**Unity target:** `No direct C# equivalent; namespace/file structure replaces it`

**Original Python excerpt:**

```python
"""Public exports for the game.entities package.

This module re-exports the core entity classes so existing imports
`from game.entities import Asteroid, XWing, ...` continue to work.

Responsibility:
- Provide a stable public API for entity types (Asteroid, Laser, Torpedo, Explosion, Player, XWing, MillenniumFalcon, Tiefighter, BattleDroid)
"""
from .asteroid import Asteroid
from .projectiles import Laser, Torpedo
from .explosion import Explosion
from .player import Player, Spieler  # Spieler kept as alias for compatibility
from .ships import XWing, MillenniumFalcon, Tiefighter, BattleDroid

__all__ = [
    'Asteroid', 'Laser', 'Torpedo', 'Explosion', 'Player', 'Spieler',
    'XWing', 'MillenniumFalcon', 'Tiefighter', 'BattleDroid'
]
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities/asteroid.py`

**Unity target:** `Gameplay/AsteroidController.cs`

**Original Python excerpt:**

```python
"""Asteroid entity module.

Responsibility:
- Represent an asteroid with animated frames, scaling and movement
- Provide collision rect and point value calculation

Public classes:
- Asteroid
"""
import pygame
import random
from game.constants import ASTEROID_SPEED_RANGE


class Asteroid:
    """Asteroid entity.

    Attributes:
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities/explosion.py`

**Unity target:** `Gameplay/ExplosionController.cs`

**Original Python excerpt:**

```python
"""Explosion visual effect entity.

Responsibility:
- Manage explosion lifetime and rendering

Public classes:
- Explosion
"""
import pygame


class Explosion:
    def __init__(self, x, y, asteroid_scale, explosion_img, window_height=None):
        self.x = x
        self.y = y
        self.asteroid_scale = asteroid_scale
        self.explosion_img = explosion_img
        self.window_height = window_height or 600
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities/player.py`

**Unity target:** `Gameplay/PlayerShipController.cs`

**Original Python excerpt:**

```python
"""Player base class and hitbox utility.

Responsibility:
- Represent a player-controlled ship with movement, lives and invulnerability
- Provide accurate hitbox calculation based on sprite alpha

Public classes:
- Player (preferred English name)
- Spieler (alias kept for compatibility with older code)
"""
import pygame

from game.constants import PLAYER_BASE_SPEED, normalize_ship_scale


class Player:
    """Base player ship class.

# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities/projectiles.py`

**Unity target:** `Gameplay/ProjectileController.cs`

**Original Python excerpt:**

```python
"""Projectile entities: Laser and Torpedo.

Responsibility:
- Simple update/draw behavior for bullets/torpedoes

Public classes:
- Laser
- Torpedo
"""
import pygame


class Laser:
    """Simple rectangular laser projectile."""

    def __init__(self, x, y, direction=-1, owner_id=None):
        self.rect = pygame.Rect(x, y, 3, 20)
        self.speed = 15
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities/ships.py`

**Unity target:** `Data/ShipDefinition.cs + Core/RuntimeContent.cs + Gameplay/ShipController.cs`

**Original Python excerpt:**

```python
"""Specialized ship classes.

Responsibility:
- Provide specific ship behaviors (shoot, torpedo) and set ship-specific speeds and scales.

Public classes:
- XWing, MillenniumFalcon, Tiefighter, BattleDroid
"""
import pygame

from .player import Player
from .projectiles import Laser, Torpedo
from game.constants import (
    SHIP_SPEED_XWING,
    SHIP_SPEED_MILLENNIUM,
    SHIP_SPEED_TIEFIGHTER,
    SHIP_SPEED_BATTLEDROID,
    SHIP_SCALE_XWING,
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities.py`

**Unity target:** `Removed as duplicated legacy layer; split across Gameplay/*`

**Original Python excerpt:**

```python
import pygame
import random
from game.constants import (
    PLAYER_BASE_SPEED,
    SHIP_SPEED_XWING,
    SHIP_SPEED_MILLENNIUM,
    SHIP_SPEED_TIEFIGHTER,
    SHIP_SPEED_BATTLEDROID,
    SHIP_SCALE_XWING,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_BATTLEDROID,
    ASTEROID_SPEED_RANGE,
)

# Adjustable gameplay values are defined in game.constants.py


# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/entities_old.py`

**Unity target:** `Not ported; legacy`

**Original Python excerpt:**

```python
# Backup of original entities module
# Kept for reference during refactor. The new game.entities package should be used instead.

import pygame
import random
from game.constants import (
    PLAYER_BASE_SPEED,
    SHIP_SPEED_XWING,
    SHIP_SPEED_MILLENNIUM,
    SHIP_SPEED_TIEFIGHTER,
    SHIP_SPEED_BATTLEDROID,
    SHIP_SCALE_XWING,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_BATTLEDROID,
    ASTEROID_SPEED_RANGE,
)

# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/highscore.py`

**Unity target:** `Save/SaveSystem.cs`

**Original Python excerpt:**

```python
"""Highscore persistence using a JSON file.

Stores a single value under the key "highscore" in a file located next to this module
(game/highscore.json). Provides simple load/save helpers and tolerates missing or
malformed files by returning 0 as a safe default.
"""

import os
import json

_HS_FILENAME = os.path.join(os.path.dirname(__file__), "highscore.json")


def load_highscore():
    """Load the stored highscore. Returns 0 if no valid score is found."""
    try:
        with open(_HS_FILENAME, "r", encoding="utf-8") as fh:
            data = json.load(fh)
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/local_pvp.py`

**Unity target:** `Multiplayer/PvpDuelSession.cs`

**Original Python excerpt:**

```python
"""Local two-player PvP mode.

Reuses the authoritative PvP world from game.pvp_duel.py.  The only things
that differ from LAN PvP are the transport/session adapter and the keyboard
input source.  No socket is created in this mode.
"""
from __future__ import annotations

from typing import Dict, List

import pygame

from game.constants import (
    LOCAL_PVP_PLAYER1_NAME,
    LOCAL_PVP_PLAYER2_NAME,
    PVP_SCORE_LIMIT_MS,
)
from game.pvp_duel import PvPDuelSession, SHIP_ASSET_KEYS
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/multiplayer.py`

**Unity target:** `Multiplayer/MultiplayerSession.cs`

**Original Python excerpt:**

```python
"""High-level multiplayer state and remote-player rendering."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional

import pygame

from game.constants import (
    SHIP_SCALE_BATTLEDROID,
    SHIP_SCALE_MILLENNIUM,
    SHIP_SCALE_TIEFIGHTER,
    SHIP_SCALE_XWING,
)
from game.network import LANClient, LANServer, LAN_PORT, MAX_PLAYERS

SHIP_SCALES = {
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/network.py`

**Unity target:** `Multiplayer/LanServer.cs + LanClient.cs + NetworkMessages.cs`

**Original Python excerpt:**

```python
"""Threaded JSON-line LAN networking for the Star Wars game.

The module contains only standard-library networking code.  The Pygame main
thread never performs blocking socket I/O: both the server and the client use
background threads plus queues for incoming/outgoing messages.
"""
from __future__ import annotations

import json
import queue
import socket
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

LAN_PORT = 48732  # Fester LAN-TCP-Port; bei Bedarf hier ändern.
NETWORK_DEBUG = True  # Für einen stillen Release-Modus auf False setzen.
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/points_fight.py`

**Unity target:** `Multiplayer/PointsFightSession.cs`

**Original Python excerpt:**

```python
"""Independent local Points Fight implementation.

Points Fight is deliberately NOT built on PvPDuelSession.  Every local player
owns a complete single-player simulation (asteroids, AI, projectiles, score and
star-system progression).  The two simulations only share the display and the
scoreboard; they never share gameplay objects or collision logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pygame

from game.background import BackgroundManager
from game.constants import (
    ASTEROID_MIN_SPAWN_INTERVAL,
    ASTEROID_SPAWN_INTERVAL,
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/pvp_duel.py`

**Unity target:** `Multiplayer/PvpDuelSession.cs (core) + LAN integration pending parity pass`

**Original Python excerpt:**

```python
"""Authoritative two-player LAN PvP duel.

The normal LAN multiplayer mode remains a lightweight state/ghost system.
PvP-Duell deliberately uses a different model: the host process owns the
shared simulation (players, projectiles, asteroids, collisions, scoring and
system transitions). Clients send only movement/fire input and render the
host snapshots. This keeps both machines on the same world without making
Pygame wait for network traffic.
"""
from __future__ import annotations

import math
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/pvp_input.py`

**Unity target:** `Multiplayer/LocalInputRouter.cs`

**Original Python excerpt:**

```python
"""Input handling used exclusively by the local two-player PvP mode.

The normal single-player and LAN modes never import or use this module.
Player 1 controls the lower ship with WASD/WS, player 2 controls the upper
ship with the arrow keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pygame

from game.constants import LOCAL_PVP_KEY_BINDINGS


@dataclass(frozen=True)
class LocalPvPPlayerInput:
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/scoreboard.py`

**Unity target:** `UI/GameHudController.cs + Canvas`

**Original Python excerpt:**

```python
"""Multiplayer live scoreboard overlay."""
from __future__ import annotations

import pygame


def draw_scoreboard(screen: pygame.Surface, players: list[dict], local_id: str | None) -> None:
    width, height = screen.get_size()
    row_h = max(30, int(min(width, height) * 0.055))
    header_h = row_h + 16
    max_rows = min(len(players), 10)
    panel_w = min(width - 60, max(480, int(width * 0.70)))
    panel_h = header_h + (max_rows + 1) * row_h + 20
    panel = pygame.Rect((width - panel_w) // 2, (height - panel_h) // 2, panel_w, panel_h)

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    screen.blit(overlay, (0, 0))
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/ui/__init__.py`

**Unity target:** `No direct C# equivalent; scene wiring replaces it`

**Original Python excerpt:**

```python
from .death import death_screen
from .faction import faction_selection
from .ship import ship_selection
from .difficulty import difficulty_selection

__all__ = ["faction_selection", "ship_selection", "difficulty_selection", "death_screen"]
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/ui/common.py`

**Unity target:** `CanvasScaler + PixelCamera`

**Original Python excerpt:**

```python
import pygame

from game.assets import set_window_icon


def resize_and_refresh(screen, width, height):
    """Create a resizeable window and keep the icon consistent."""
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    set_window_icon()
    return screen
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/ui/death.py`

**Unity target:** `UI/DeathScreenController.cs`

**Original Python excerpt:**

```python
import sys

import pygame

from game.assets import set_window_icon
from game.constants import BLACK
from game.highscore import load_highscore, save_highscore


def death_screen(screen, clock, score, WIDTH, HEIGHT):
    """Show death screen and return True to restart or False to quit.

    The function loads the personal highscore from disk, updates it if the
    current score is higher and persists the new record. The death screen
    displays the current points and the personal record.
    """
    personal_record = load_highscore()
    new_record = False
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/ui/difficulty.py`

**Unity target:** `UI/DifficultySelectionController.cs`

**Original Python excerpt:**

```python
import sys
import pygame
from game.assets import set_window_icon


DIFFICULTIES = [
    ("easy", "Einfach", "Weniger und langsamere Gegner"),
    ("normal", "Normal", "Ausgewogene Herausforderung"),
    ("hard", "Schwer", "Stärkere und aggressivere Gegner"),
    ("expert", "Experte", "Für erfahrene Spieler"),
]


def difficulty_selection(screen, clock, width, height, default="normal"):
    """Select the game difficulty before the ship selection."""
    selected = next((i for i, item in enumerate(DIFFICULTIES) if item[0] == default), 1)

    while True:
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/ui/faction.py`

**Unity target:** `UI/FactionSelectionController.cs`

**Original Python excerpt:**

```python
import sys

import pygame

from game.assets import set_window_icon


def faction_selection(screen, clock, width, height, rebel_logo_img, empire_logo_img):
    """Show the faction choice and return the choice plus the active window size."""
    while True:
        card_width = int(width * 0.32)
        card_height = int(height * 0.45)
        rebel_rect = pygame.Rect(int(width * 0.15), int(height * 0.28), card_width, card_height)
        empire_rect = pygame.Rect(int(width * 0.53), int(height * 0.28), card_width, card_height)

        font = pygame.font.Font(None, max(24, int(min(width, height) * 0.05)))
        small_font = pygame.font.Font(None, max(18, int(min(width, height) * 0.035)))
        title_font = pygame.font.Font(None, max(28, int(min(width, height) * 0.08)))
# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/ui/multiplayer.py`

**Unity target:** `UI/MultiplayerMenuController.cs + Canvas wiring`

**Original Python excerpt:**

```python
"""Pygame menus for LAN multiplayer."""
from __future__ import annotations

import pygame

from game.network import LAN_PORT


def _draw_button(screen, rect, text, font, hover=False, enabled=True):
    fill = (0, 150, 220) if hover and enabled else (36, 42, 62)
    border = (120, 220, 255) if enabled else (90, 90, 90)
    text_color = (255, 255, 255) if enabled else (130, 130, 130)
    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, border, rect, 2, border_radius=14)
    label = font.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=rect.center))


# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

## `game/ui/ship.py`

**Unity target:** `UI/ShipSelectionController.cs`

**Original Python excerpt:**

```python
import sys

import pygame

from game.assets import set_window_icon


def _uniform_preview_scale(image, max_width, max_height):
    if image is None:
        return 1.0

    width, height = image.get_size()
    if width <= 0 or height <= 0:
        return 1.0

    return min(max_width / width, max_height / height)


# ... (original file continues)
```

**Porting note:** Unity moves this responsibility out of the Pygame loop and into the listed MonoBehaviour/data/service class(es). Collision/rendering/time/input calls are translated through the Unity equivalents in `MIGRATION_PLAN.md`.

