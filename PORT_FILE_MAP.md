# Python → Unity file map

| Python file | Responsibility | Unity target |
|---|---|---|
| `StarWarsGame.py` | root launcher | `Core/GameBootstrap.cs`, scene flow |
| `game/StarWarsGame.py` | main loop + flow | `Core/GameSession.cs`, `UI/*`, multiplayer controllers |
| `game/constants.py` | balancing | `Core/GameConstants.cs` |
| `game/assets.py` | asset load | `Core/AssetLibrary.cs` |
| `game/entities/player.py` | player movement/lives/hitbox | `Gameplay/PlayerShipController.cs` |
| `game/entities/ships.py` | 4 ship classes | `Data/ShipDefinition.cs`, `Core/RuntimeContent.cs` |
| `game/entities/projectiles.py` | laser/torpedo | `Gameplay/ProjectileController.cs` |
| `game/entities/asteroid.py` | animated asteroids | `Gameplay/AsteroidController.cs` |
| `game/entities/explosion.py` | explosion lifetime | `Gameplay/ExplosionController.cs` |
| `game/entities.py` | old combined entities | removed; split targets above |
| `game/entities_old.py` | old asteroid | not ported |
| `game/enemies/config.py` | enemy definitions | `Data/EnemyArchetype.cs`, `Core/RuntimeContent.cs` |
| `game/enemies/movement.py` | steering | `Gameplay/EnemyMovement.cs` |
| `game/enemies/ai.py` | tactical decisions | `Gameplay/EnemyBrain.cs` |
| `game/enemies/projectiles.py` | AI projectiles | `Gameplay/ProjectileController.cs` |
| `game/enemies/weapons.py` | AI weapons | `Gameplay/EnemyWeaponSystem.cs` |
| `game/enemies/base.py` | enemy entity | `Gameplay/EnemyController.cs` |
| `game/enemies/manager.py` | spawning/collisions/unlocks | `Gameplay/EnemyManager.cs` |
| `game/background/systems.py` | star-system definitions | `Data/StarSystemDefinition.cs` |
| `game/background/system_manager.py` | randomized system order | `Gameplay/Background/StarSystemManager.cs` |
| `game/background/objects.py` | stars/planets/foreground | `Gameplay/Background/StarfieldController.cs`, `PlanetController.cs` |
| `game/background/starfield.py` | parallax stars | `Gameplay/Background/StarfieldController.cs` |
| `game/background/planet_manager.py` | planet spawning | `BackgroundManager.cs` + `PlanetController.cs` |
| `game/background/transition_manager.py` | galaxy-map transition | `BackgroundManager.cs` (transition layer) |
| `game/background/manager.py` | visual coordinator | `Gameplay/Background/BackgroundManager.cs` |
| `game/ui/faction.py` | faction menu | `UI/FactionSelectionController.cs` |
| `game/ui/difficulty.py` | difficulty menu | `UI/DifficultySelectionController.cs` |
| `game/ui/ship.py` | ship menu | `UI/ShipSelectionController.cs` |
| `game/ui/death.py` | death screen | `UI/DeathScreenController.cs` |
| `game/ui/multiplayer.py` | multiplayer menus/lobby | `UI/MultiplayerMenuController.cs` + Canvas prefabs |
| `game/ui/common.py` | resizing helpers | Canvas Scaler / PixelCamera |
| `game/highscore.py` | JSON score persistence | `Save/SaveSystem.cs` |
| `game/scoreboard.py` | score drawing | `UI/GameHudController.cs` + Canvas |
| `game/pvp_input.py` | local 2-player keys | `Multiplayer/LocalInputRouter.cs` |
| `game/points_fight.py` | isolated worlds | `Multiplayer/PointsFightSession.cs` |
| `game/local_pvp.py` | local PvP transport adapter | `Multiplayer/PvpDuelSession.cs` |
| `game/pvp_duel.py` | host-authoritative PvP | `Multiplayer/PvpDuelSession.cs` + LAN controller |
| `game/network.py` | threaded TCP protocol | `Multiplayer/LanServer.cs`, `LanClient.cs`, `NetworkMessages.cs` |
| `game/multiplayer.py` | remote cache/session | `Multiplayer/MultiplayerSession.cs` |
