# Star Wars – Pygame → Unity Migration Plan

## 1. Current Python architecture

The uploaded project contains 40+ Python modules around these subsystems:

- `game/StarWarsGame.py`: application/game-flow coordinator, menu routing, singleplayer loop, multiplayer routing.
- `game/constants.py`: global balancing and network constants.
- `game/assets.py`: Pygame image loading and icon setup.
- `game/entities/*`: Player, four ships, asteroids, projectiles and explosions.
- `game/enemies/*`: data-driven archetypes, movement, tactical AI, enemy weapons and manager.
- `game/background/*`: starfield, planets, foreground objects, randomized system order and system transitions.
- `game/ui/*`: faction, difficulty, ship and multiplayer menus plus death screen.
- `game/network.py`: threaded TCP + JSON-line LAN transport.
- `game/multiplayer.py`: lobby/remote-player abstraction.
- `game/points_fight.py`: two completely isolated singleplayer simulations shown side by side.
- `game/pvp_duel.py`: host-authoritative PvP simulation, snapshots, respawn, projectiles and scoring.
- `game/local_pvp.py` / `game/pvp_input.py`: local keyboard adapter for the same PvP rules.
- `game/highscore.py`: JSON high-score persistence.
- `game/scoreboard.py`: score table rendering.

### Runtime flow

`main()` → `main_menu()` → either singleplayer flow or multiplayer flow.

Singleplayer:
`Faction → Difficulty → Ship → run_game_session()`.

During `run_game_session()`:
`Player → Projectiles → Asteroids → EnemyManager → BackgroundManager → HUD`.

Multiplayer:
`Lobby → READY → Countdown → either Points Fight or PvP Duel`.

## 2. Unity target architecture

Unity uses the same responsibilities but replaces runtime primitives:

| Python/Pygame | Unity |
|---|---|
| `pygame.display` | Scene + Camera + Canvas |
| `pygame.Surface` | Sprite / Texture2D / RenderTexture |
| `pygame.sprite` | GameObject + MonoBehaviour |
| `pygame.Rect` | Collider2D / Bounds / Rect logic |
| `pygame.time.get_ticks()` | `Time.unscaledTime` / `Time.deltaTime` |
| `pygame.event` | Unity Input System |
| `pygame.key.get_pressed()` | `Keyboard.current` / Input Actions |
| `pygame.mixer` | `AudioSource` / `AudioMixer` |
| `pygame.draw` | SpriteRenderer / UI / GL helper |
| Pygame main loop | Unity lifecycle (`Update`, `LateUpdate`, render pipeline) |
| `json` files | Unity JSON + `Application.persistentDataPath` |
| Python TCP threads | C# `TcpListener` / `TcpClient` + worker threads |

## 3. Important architecture fixes carried into the port

1. The root `StarWarsGame.py` and `game/StarWarsGame.py` duplicate responsibilities. Unity has one flow controller.
2. `game/entities.py` duplicates the newer `game/entities/` package. Unity has one authoritative entity layer.
3. `game/entities_old.py` is treated as legacy and is not ported.
4. The current Python `game/StarWarsGame.py` imports `LocalPointsFightSession` from `game.local_pvp`, although that class is defined in `game.points_fight`. Unity uses a single `PointsFightSession` target.
5. Rendering and gameplay are separated. This prevents the Unity version from reproducing the Pygame coupling between simulation and `blit()` calls.
6. All gameplay numbers remain centralized in `GameConstants`/data objects.
7. LAN transport is isolated from game simulation, so local multiplayer never needs a socket.

## 4. Migration order

### Phase 1 – already ported in this package

- constants/balancing
- pixel coordinate adapter
- asset loading model
- ship/player model
- laser/torpedo model
- asteroids
- explosions
- enemy movement
- enemy tactical AI
- enemy weapons
- enemy manager
- star systems / starfield / planets / background
- main singleplayer session
- HUD/menu controllers
- inventory / items
- quests
- save system
- reusable combat service
- TCP LAN transport
- local Punktekampf and Letzter-Überlebender session scaffolds

### Phase 2 – scene/prefab authoring in Unity Editor

- import Pixelarts as Sprites with Pixels Per Unit = 1 and Filter Mode = Point
- create Player/Enemy/Asteroid/Projectile prefabs
- create Canvas/HUD prefabs
- create six gameplay/menu scenes
- wire serialized references
- add Input System package

### Phase 3 – final parity pass

- parity-test spawn timing against 60 FPS Pygame behavior
- verify ship hitboxes from sprite alpha
- verify enemy unlock warnings
- verify every star-system transition
- verify LAN snapshot frequency and host disconnect behavior

## 5. Systems that were not present in the Python project

Inventory, item, quest and generic combat subsystems do **not** exist in the uploaded Python code. Unity therefore provides them as isolated, optional systems. They do not alter the existing arcade-loop rules until explicitly connected to a game mode.
