# Unity setup

## Recommended project type

Create a **2D Core** Unity project and copy this `Assets/` folder into it.

Install the **Input System** package via Package Manager.

## Pixel-art import settings

For every file under `Assets/Resources/Pixelarts/`:

- Texture Type: Sprite (2D and UI)
- Sprite Mode: Single
- Pixels Per Unit: **1**
- Filter Mode: **Point (no filter)**
- Compression: None
- Generate Mip Maps: Off

This keeps the Python pixel measurements close to Unity screen units.

## Required scene names

- `MainMenu`
- `FactionSelection`
- `DifficultySelection`
- `ShipSelection`
- `Singleplayer`
- `MultiplayerMenu`
- `LocalPointsFight`
- `LocalLastSurvivor`
- `LanLobby`

## Singleplayer hierarchy

```text
Singleplayer
├── Main Camera (PixelCamera)
├── Systems
│   ├── AssetLibrary
│   ├── BackgroundManager
│   ├── StarSystemManager
│   ├── StarfieldController
│   └── EnemyManager
├── GameSession
├── Player prefab instance
└── HUD Canvas
    └── GameHudController
```

The player and enemy prefabs need `SpriteRenderer` + `Collider2D` and their relevant controller component.

## Input

The current scripts intentionally use the Unity Input System's `Keyboard.current` API so the controls stay close to the original Pygame bindings without recreating `pygame.event`.

Singleplayer controls remain:

- A/D or Left/Right: move
- Space/W/Up: laser
- S/Down: torpedo

## Multiplayer

LAN transport uses TCP on port `28000`. It is deliberately standard-library-only and does not require an external game server.

## Inventory / Quests / Save

These are optional systems because the Python project did not contain them. Attach `InventorySystem`, `QuestSystem` and `SaveGameCoordinator` to a persistent gameplay root when you decide to use them.
