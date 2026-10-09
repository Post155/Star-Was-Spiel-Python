# Port status / honesty check

## Implemented in this first pass

- Centralized gameplay constants and difficulty profiles.
- Pixel-space adapter preserving the original 800x600 coordinate model.
- Four player ships and their weapon muzzle rules.
- Player movement, 3 lives and 2 s invulnerability.
- Laser + torpedo projectiles.
- Animated asteroids with original point values.
- Enemy archetypes, unlock thresholds, role selection, steering, tactical dodge, aiming, bursts and torpedoes.
- Randomized star-system order with EARTH fixed as the first system.
- Starfield parallax and planet spawning.
- Singleplayer session coordinator and HUD controller.
- Inventory, item, quest, save and high-score services as new Unity-only systems.
- Local multiplayer input abstraction.
- LAN TCP server/client transport with JSON messages.
- Local Points Fight and Local Last Survivor session foundations.

## Not yet Unity-editor-verified

This environment does not contain the Unity Editor, so the package has not been compiled/run inside Unity. The C# source was statically checked for balanced braces and duplicate class names, but Unity-specific serialization and scene wiring still need Editor validation.

The following are specifically flagged for the next parity pass:

1. Exact alpha-mask hitbox calculation from the Python sprites should be implemented as an import/build step or cached SpriteShape/PolygonCollider2D data rather than the current proportional Collider2D fallback.
2. LAN PvP snapshot authority still needs to be wired from `LanServer` message queues into a fully authoritative `PvpDuelSession` host state. The transport itself is present.
3. The Python galaxy-map transition currently contains a richer render sequence; Unity currently has the transition timing/background overlay but not a pixel-identical UI recreation.
4. Unity Canvas scenes/prefabs must be authored and references assigned in the Editor.
5. The Python renderer is frame-based for several systems; the Unity version deliberately keeps those values but uses `Time.deltaTime` for AI/network/game-state updates. A final frame-parity tuning pass is therefore still required.
