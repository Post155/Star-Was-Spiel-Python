# Datei-für-Datei-Migration

Legende Status: **Sim** = portiert und automatisiert getestet · **Unity** = portiert, nur kompiliert (nicht in Unity gespielt) · **entfällt** = bewusst nicht portiert · **neu** = nicht im Original.
Alle Pfade der C#-Dateien relativ zu `Assets/Scripts/`.

## Einstieg

### `StarWarsGame.py` (Root, 848 Z.) – Hauptschleife, Menüfluss, Einzelspieler, LAN-/Lokal-Flows
* Klassen/Funktionen: `main`, `run_game_session`, `run_multiplayer_flow`, `run_pvp_flow`, `run_local_points_flow`, `run_local_pvp_flow`, Schiffsfabrik.
* Unity: `Game/SceneBootstrap.cs` (Szenen-Start), `Game/AppState.cs` (Menüfluss `AfterFaction/AfterDifficulty/AfterShip`), `Game/GameControllers.cs` (`SinglePlayerController`, `PointsFightController`, `PvpController`, `LanPointsController`), `Game/LobbyController.cs`, `Sim/World/SinglePlayerWorld.cs` (Inhalt von `run_game_session`).
* Unterschiede: Pygame-Schleife → fester 60-Hz-Tick in `SinglePlayerWorld.Step`; Debug-Tasten H und 1–4 erhalten; `ESC` führt ins Hauptmenü. Reihenfolge je Frame wie im Original: Schüsse → Bewegung → Projektile → Asteroiden → Kollisionen → Gegner → Hintergrund.

### `game/StarWarsGame.py` (894 Z.) – ältere, defekte Kopie
* **entfällt.** `ImportError` (`LocalPointsFightSession` aus `game.local_pvp`), nicht existierendes `draw_live_ranking`, veraltete Signaturen. Siehe `MIGRATION_PLAN.md`.

### `game/__init__.py`, `game/ui/__init__.py` – leer/Reexports → entfallen.

## Konstanten und Assets

### `game/constants.py` (263 Z.)
* Inhalt: Fenster, Schiffsgeschwindigkeiten, `DIFFICULTY_SETTINGS`, Freischaltpunkte, Systemwechsel, PvP-/Netzwerk-Konstanten, `LOCAL_PVP_KEY_BINDINGS`, Skalierungshelfer.
* Unity: `Sim/Core/GameConstants.cs` (inkl. `Difficulties`, `DifficultyProfile`), `Game/InputProvider.cs` (Tastenbelegung).
* Unterschiede: Alle Werte übernommen; Golden-Test belegt Schwierigkeitsableitungen (312 Kombinationen). Fenstergröße ist logisch 800×600 (Letterbox).

### `game/assets.py` (146 Z.) – Laden/Normalisieren der Bilder, Planetenentdeckung
* Unity: `Game/SpriteLibrary.cs` (Resources-Laden, Point-Filter, Platzhalter), `Sim/Background/StarSystems.cs` (`PlanetCatalog`), `Sim/Data/AssetMetrics.cs` (aus echtem Pygame gemessen).
* Unterschiede: Die Normalisierung der Planetennamen wurde einmalig ausgewertet und fest als Katalog hinterlegt (13 Planeten); fehlende Bilder → magentafarbener Platzhalter + Warnung.

## Entitäten

### `game/entities/ships.py`, `player.py` (99 + 137 Z.) – `Player`, `XWing`, `MillenniumFalcon`, `Tiefighter`, `BattleDroid`
* Unity: `Sim/Entities/PlayerShip.cs`, `Sim/Data/ShipCatalog.cs`.
* Übernommen: Geschwindigkeiten 12/14/11/12, Referenzhöhe 96, Laser-Offsets, Torpedo nur X-Wing/TIE, 3 Leben, 2 s Unverwundbarkeit, 200-ms-Blinken, Alpha-Hitbox, Grenzen. TIE wird – wie im Original – um 180° gedreht dargestellt.
* Test: Position, Hitbox, Laser- und Torpedo-Rechtecke für alle 4 Schiffe (links/rechts/Rand) stimmen mit Python überein.

### `game/entities/projectiles.py` (52 Z.) – `Laser` (3×20, 15 px/Frame), `Torpedo` (Skala 0,5, 10 px/Frame)
* Unity: `Sim/Entities/Projectiles.cs`. PvP-Erweiterung: Richtung ±1, Besitzer-ID, Projektil-ID (Original ebenfalls in `pvp_duel`).

### `game/entities/asteroid.py` (108 Z.), `explosion.py` (41 Z.)
* Unity: `Sim/Entities/Asteroid.cs` (`Asteroid`, `Explosion`).
* Übernommen: Skalen {0,25;0,5;0,75;1}·Multiplikator, Clamp 0,18–1,25, Geschwindigkeit `randint(2,8)·Mul`, Animation (12 Frames, alle 5 Ticks), 70-%-Kollisionsrechteck, Punkte 100/75/50, Explosion 20 Frames.

### `game/entities.py` (327 Z.), `game/entities_old.py` (24 Z.) – veraltet/verdeckt → **entfällt**.

## Gegner

### `game/enemies/config.py` (153 Z.) – Archetypen standard/fast/heavy/elite → `Sim/Enemies/EnemyArchetype.cs`
### `game/enemies/ai.py` (126 Z.) → `EnemyBrain` in `Sim/Enemies/EnemyShip.cs` (Rollen, Reaktionstimer, Ausweichen, Zielvorhersage)
### `game/enemies/movement.py` (50 Z.) → `EnemyMovement` (Beschleunigungsbegrenzung). **Golden-Test:** 160-Tick-Trajektorie je Archetyp identisch (1e-9).
### `game/enemies/weapons.py` (94 Z.), `projectiles.py` (64 Z.) → `EnemyWeaponSystem`, `Sim/Enemies/EnemyProjectiles.cs` (Salven, Torpedos, Trefferstreuung, Geschwindigkeit in px/s)
### `game/enemies/base.py` (159 Z.) → `EnemyShip` (HP, Rüstung, Flash, Hitbox aus Metriken). Unterschied: Flash als Rot-Tönung statt additivem Weiß.
### `game/enemies/manager.py` (409 Z.) → `Sim/Enemies/EnemyManager.cs`
* Übernommen: Freischaltung (Tier 1–3), Warnungen (2,5 s, Spawnsperre), Intervalle, Maximalzahl, Archetyp-Auswahl, Balancing je Schwierigkeit/System, Rollenverteilung, Spielerschüsse (Laser 1, Torpedo 4), Gegnerschüsse, Schiffskollision, Explosionen.
* Test: Golden (Skalierung, Max, Intervall, Tier, balancierte Archetypen) + Ablauf-Tests.
* Original-Quirk (Spawn am linken Rand) bewusst beibehalten.

## Hintergrund

### `game/background/systems.py` (179 Z.), `system_manager.py` (104 Z.) → `Sim/Background/StarSystems.cs`
* 12 Systeme, EARTH fix zuerst, Rest gemischt; Asteroiden-Tempo, Sterndichte, Filterfarben. Planetenfallback für BLACKHOLE/TODESSTERN/STERNZERSTÖRER wie im Original.
### `game/background/starfield.py`, `objects.py`, `planet_manager.py`, `manager.py`, `transition_manager.py` → `Sim/Background/BackgroundDirector.cs` (Sterne, Planeten, Vordergrund, Systemwechsel nach 2000 Punkten oder 30 s, Karten-Überblendung 5 s, Planetenfenster 10–20 s) und `Game/Stage.cs` (`BackgroundView`: Darstellung).
* Unterschiede: Der Systemwechsel wird am Ende von `Update` abgeschlossen (im Original im `draw`-Aufruf desselben Frames). Die Überblendung ist vereinfacht (Dimmung, Linie, Kreise, Namen, 1 Planet-Thumbnail je Seite, „ZIELSYSTEM ERREICHT“). Die `Hyperraum`-Animation (14 s) wird im Original nur im Sync-Code erwähnt, im Spiel nicht angezeigt → nicht portiert.

## Spielmodi

### `game/points_fight.py` (403 Z.) – lokaler Punktekampf → `Sim/World/PointsFightMatch.cs`, `Game/GameControllers.cs` (`PointsFightController`)
* Zwei getrennte `SinglePlayerWorld`-Instanzen (eigene Uhr, Listen, Zufall); 180 s oder beide tot; TAB-Rangliste; Ghost des Gegners.
* Korrektur: Asteroiden-Geschwindigkeitsmultiplikator wirkt (Original-Bug). Ghost-Größe = tatsächliche Schiffsgröße (Original: Skalierungstabelle).
### `game/local_pvp.py` (247 Z.) – `LocalPvPTransport`, `LocalPvPDuelSession` → `PvpWorld.Step` direkt (kein Transport nötig) + `PvpController` (Kind `Local`).
### `game/pvp_input.py` (83 Z.) → `Game/InputProvider.cs` (`ControlScheme.Player1Wasd/Player2Arrows`).
### `game/pvp_duel.py` (1 464 Z.) → `Sim/World/PvpWorld.cs` (Host-Simulation, Snapshot), `Sim/Net/PvpNet.cs` (`PvpClientView`, `PvpHostDriver`, `PvpClientDriver`), `Game/PvpView.cs` (Darstellung/Perspektive), `GameControllers.cs` (Ergebnisbildschirm).
* Übernommen: Rollen unten/oben, Geschwindigkeit 12, Schaden Laser 1/Torpedo 2, 150 Treffer-/1000 Kill-Punkte, Respawn 900 ms + 2 s Schutz, Lane-Asteroiden (max. 36, Sicherheitsabstand 130 px), Systemwechsel mit Löschen von Asteroiden/Projektilen, Snapshot-Format, Ergebnis/Statistik, 180-s-Punkteregel.
* Korrektur: doppelte `_update_host_asteroids`-Definition (siehe Plan).
* Neu: `HitLedger` (ein Projektil wirkt höchstens einmal).

## Netzwerk

### `game/network.py` (714 Z.) → `Sim/Net/LanServer.cs`, `LanClient.cs`, `Protocol.cs`, `Json.cs`
* Port 48732, JSON-Lines, Protokollversion 1, Phasen lobby/setup/countdown/game, Spielmodi points/pvp, Nachrichten wie im Original.
* Erweiterungen (additiv): `host`-Flag im `hello` (Host nur über Loopback), `remaining_ms` im `countdown`, `alive` in `points_state`/Snapshot, Sequenz-/Raten-Validierung für `pvp_fire`, Phasenprüfung. Der Spielmodus `lan` (ungenutzter Alt-Modus) entfällt.
### `game/multiplayer.py` (286 Z.) → `Sim/Net/MultiplayerSession.cs` (Host/Join, Ghosts, Rangliste)

## Persistenz und Anzeige

### `game/highscore.py` (42 Z.) → `Sim/Save/SaveService.cs` (+ Import des alten `highscore.json`)
### `game/scoreboard.py` (63 Z.) → Rangliste in `GameControllers.cs` (`RankText`, `BoardText`) – als Textpanel statt Pygame-Tabelle.
### `game/ui/common.py` (10 Z.) → `Game/Ui.cs`
### `game/ui/faction.py`, `difficulty.py`, `ship.py`, `death.py` → `Game/MenuScreens.cs`, `GameControllers.cs` (`ShowDeath`)
* Texte („GAME OVER“, „DEINE PUNKTZAHL“, „PERSÖNLICHER REKORD“, „NEUER REKORD!“, Schwierigkeitsbeschreibungen) übernommen; Layout an uGUI angepasst (Buttons plus Zifferntasten). `ESC` im Schwierigkeitsmenü liefert im Original die aktuelle Auswahl – im Port führt es zurück.
### `game/ui/multiplayer.py` (522 Z.) → `MenuScreens.cs` (Mehrspieler-Menü, Regelwahl, LAN-Formular), `Game/LobbyController.cs` (Lobby/Countdown)
* Unterschied: Der Spieler-Hinweis vor der lokalen Auswahl („Spieler 1 – Steuerung …“) steht als Kopfzeile der Auswahlmenüs.

## Neu (kein Original)

| Datei | Inhalt |
|---|---|
| `Sim/Systems/Items.cs` | `ItemDefinition`, `ItemDatabase`, `Inventory` |
| `Sim/Systems/Quests.cs` | `QuestLog`, `QuestDefinition` |
| `Sim/Systems/CombatSystem.cs` | Rüstungsformel, `HitLedger` |
| `Game/SoundBank.cs` | synthetisierte Effekte |
| `Game/Data/ContentAssets.cs` | ScriptableObject-Klassen, `ContentLoader` |
| `Editor/StarWarsEditorTools.cs` | Menü „Star Wars“ |
| `Tests/…` | Testsuite, Konsolen-Runner, Golden-Daten |
