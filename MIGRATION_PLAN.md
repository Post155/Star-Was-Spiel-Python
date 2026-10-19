# Migrationsplan und Designentscheidungen

## 1. Ausgangslage (Analyse)

Untersucht wurden das komplette Python-Original (9 397 Zeilen in 45 Dateien) und der Vorgängerport (47 C#-Dateien, ca. 2 400 Zeilen).

### Befunde im Python-Original

| # | Befund | Entscheidung im Unity-Port |
|---|---|---|
| 1 | **Zwei Einstiegspunkte.** Die Root-`StarWarsGame.py` (laut README der Startpunkt) ist korrekt; `game/StarWarsGame.py` ist eine ältere, abweichende Kopie. | Maßgeblich ist die Root-Datei. |
| 2 | **Importfehler:** `game/StarWarsGame.py` importiert `LocalPointsFightSession` aus `game.local_pvp`. Dort existiert die Klasse nicht (`local_pvp.py` enthält nur `LocalPvPTransport`/`LocalPvPDuelSession`); sie liegt in `game/points_fight.py`. Dieselbe Datei ruft zudem `scoreboard.draw_live_ranking` auf, das es nicht gibt, und nutzt eine veraltete Konstruktor-Signatur. | Nicht übernommen. Es gibt genau eine Implementierung (`PointsFightMatch`). |
| 3 | Doppelte/veraltete Module: `game/entities.py` (327 Z.) wird vom Paket `game/entities/` verdeckt, `entities_old.py` ist ein Stub. | Nicht portiert; das Paket ist maßgeblich. |
| 4 | README nennt andere Zahlen (z. B. Freischaltung 1000/3000/6000) als `constants.py` (2000/5000/10000). | `constants.py` ist maßgeblich (und per Golden-Test belegt). |
| 5 | `PvPDuelSession._update_host_asteroids` ist **zweimal** definiert; die zweite Definition (entfernt nur Asteroiden mit `y > Höhe`) verdeckt die erste. Seitlich/oben davonfliegende Lane-Asteroiden würden nie entfernt und füllen die Obergrenze von 36. | Port nutzt die beabsichtigte Bereichsprüfung in alle Richtungen (dokumentierte Korrektur, per Test belegt). |
| 6 | `PointsFightWorld._create_asteroid` setzt `asteroid.speed` nachträglich, `Asteroid.update` nutzt aber `vy` aus dem Konstruktor ⇒ Geschwindigkeits-Multiplikator wirkt im lokalen Punktekampf **nicht**. | Alle Modi nutzen dieselbe Weltsimulation wie der Einzelspieler (Multiplikatoren wirken überall). Dokumentierte Korrektur. |
| 7 | Gegner-Spawn: `approx_width` nutzt die **unskalierte** Bildbreite (`ship_scale = 1`, ca. 1100 px) ⇒ Gegner spawnen praktisch immer am linken Rand (x = 12). | 1:1 übernommen (Originalverhalten), im Code kommentiert. |
| 8 | Systeme `BLACKHOLE`, `TODESSTERN`, `STERNZERSTÖRER` haben im Original **keinen** Planetenschlüssel (Asset-Namen passen nicht zu den Systemschlüsseln) ⇒ Fallback: zufälliges Bild aus allen 13 Planeten. | 1:1 übernommen (per Test belegt); der Vorgängerport hatte feste Planeten. |
| 9 | Countdown: `started_at` ist absolute Epoch-Zeit des Hosts; Clients vergleichen mit ihrer lokalen Uhr. | Zusätzliches Feld `remaining_ms` (uhrenunabhängig); `started_at` bleibt für Kompatibilität. |
| 10 | LAN-Punktekampf: Clients melden Punkte selbst (kein „alive“-Feld, kein Zeitlimit in der Root-Version). | Beibehalten (reine Anzeige/Ghost-Daten). Zusätzlich optionales Feld `alive` für „GAME OVER“ in der Rangliste. |
| 11 | Das Original enthält weder Inventar, Items, Quests, ein Kampf-Framework noch Audio. | Neue Systeme sind als **neu** gekennzeichnet (Abschnitt 4). |

### Befunde im Vorgängerport (Unity)

| # | Befund |
|---|---|
| 1 | Nutzt `UnityEngine.InputSystem` und `UnityEngine.UI`, obwohl **weder** `com.unity.inputsystem` **noch** `com.unity.ugui` im Manifest stehen und der Input-Handler auf „Legacy“ steht ⇒ Kompilierfehler. |
| 2 | PNG-Importer stehen auf *Default/Bilinear/Mipmaps/PPU 100*, nicht auf *Sprite* ⇒ `Resources.Load<Sprite>` liefert `null`, Pixelart wäre unscharf. |
| 3 | Keine Szenen, keine Prefabs, leere Build Settings. |
| 4 | LAN-Port 28000 statt 48732; LAN/PvP laut eigener `PARITY_STATUS.md` nicht mit der Spielsimulation verbunden. |
| 5 | Asteroiden-Spawn pro Unity-`Update` (framerate-abhängig); feste Planeten für alle Systeme; Hitboxen nur als Proportions-Näherung. |
| 6 | Doppeltes PNG mit zerstörtem Dateinamen (Sternzerstörer). |

## 2. Architektur

```
┌────────────────────────── Unity-Schicht (Assets/Scripts/Game) ──────────────────────────┐
│ SceneBootstrap → MenuScreens / LobbyController / *Controller   (Eingabe, UI, Audio)    │
│ Stage + SpritePool + WorldView/PvpView/BackgroundView          (Darstellung)           │
└───────────────▲──────────────────────────────────────────────────────────────────────────┘
                │ liest Zustand, ruft Step(Input) im festen 60-Hz-Takt auf
┌───────────────┴────────────── Sim (Assets/Scripts/Sim, reines C#) ──────────────────────┐
│ World:   SinglePlayerWorld · PointsFightMatch · PvpWorld                                 │
│ Enemies: EnemyManager · EnemyShip (Brain/Movement/Weapons) · Archetypen                  │
│ Background: BackgroundDirector · SystemManager · Sterne/Planeten/Vordergrund             │
│ Entities: PlayerShip · Laser/Torpedo · Asteroid · Explosion                              │
│ Net: LanServer · LanClient · MultiplayerSession · PvpHostDriver/PvpClientDriver · Json   │
│ Systems: Inventory · Items · QuestLog · CombatSystem   Save: SaveService                 │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

Warum zwei Schichten? (1) Die Spielregeln lassen sich ohne Unity kompilieren und **gegen den echten Python-Code testen**. (2) Es gibt keine MonoBehaviour-„Riesenklasse“; Datenmodelle, Logik, Darstellung, Eingabe, Netzwerk und Speicherung sind getrennt. (3) Jede Welt ist eine eigene Instanz ⇒ der Punktekampf kann nichts teilen.

## 3. Zentrale Entscheidungen

| Thema | Entscheidung | Grund |
|---|---|---|
| Zeitbasis | Fester **60-Hz-Tick** (Akkumulator, max. 5 Ticks/Frame) mit `dt = 1/60`. Pygame-Mechaniken sind framebasiert (Asteroiden, Projektile) bzw. dt-basiert mit `dt ≈ 1/60` (KI) – beides bleibt identisch. | Verhalten unabhängig von der Bildwiederholrate, 1:1-Parität. |
| Uhr | Jede Welt hat eine `SimClock` (ms), die pro Tick um 1000/60 wächst (statt `pygame.time.get_ticks()`). | Unverwundbarkeit, Respawn, Systemwechsel sind deterministisch und testbar. |
| Koordinaten | Pygame-Pixel (oben links, y nach unten) in der Simulation; `Stage.P()` rechnet nach Unity (y nach oben). | Formeln des Originals bleiben unverändert. |
| `pygame.Rect` | Eigene Struktur `RectI` mit Pygame-Semantik (Float-Abschneiden, `center` rundet, `colliderect`). `pygame.transform.scale_by` schneidet ab. | Am Original gemessen (Torpedo-Rechteck des TIE weicht sonst um 1 px ab). |
| Hitboxen | Alpha-Bounding-Boxen und Sprite-Größen wurden mit **echtem Pygame** aus den Bildern gemessen und als `AssetMetrics` eingebettet. | Unabhängig von Unity-Import-Einstellungen, exakt wie das Original. |
| Auflösung | Logische Spielfläche **800×600**, Letterbox im Fenster; Punktekampf je Welt 400×600. | Gleiche Spielbalance bei jeder Auflösung (das Original ist skalierbar, verändert aber das Spielfeld). |
| Zufall | `ISimRandom` (austauschbar) | Deterministische Tests. |
| Highscore/Speicher | JSON in `persistentDataPath`, atomar (temp → ersetzen), `.bak`, `.corrupt`, Versionsfeld, Import des alten Highscores. | Robustheit bei Abbruch/Beschädigung. |
| JSON | Eigener minimaler Parser/Writer. | Unity-unabhängig, thread-sicher, keine Paketabhängigkeit. |
| Netzwerk | TCP, JSON-Lines, Port **48732**, Protokollversion 1, Nachrichtenformat des Originals; Erweiterungen sind additiv (`host`, `remaining_ms`, `alive`). | Kompatibilität, siehe Abschnitt 5. |
| UI | uGUI per Code aufgebaut; Szenen enthalten nur Kamera + Bootstrap. | Keine manuelle Inspector-Verdrahtung nötig. |
| ScriptableObjects | Nur Items sind laufzeitrelevant; Schiffe/Gegner/Systeme sind Inspektions-Exporte. | Zwei Datenquellen für Spielwerte würden die Paritätsprüfung entwerten. |
| asmdef | Nur `StarWars.Sim` (+ Tests). | Vermeidet Referenzfehler auf `UnityEngine.UI` in unbekannten Unity-Versionen. |

## 4. Neue Systeme (nicht im Original)

* **Inventar** (12 Slots, Stapelgrößen, Kapazität, Ereignis `Changed`), **Items** (datengetrieben, 5 Kategorien), **QuestLog** (annehmen, Fortschritt über Spielereignisse, Abschluss, Belohnung genau einmal, Speicherung).
* **CombatSystem**: zentrale Rüstungsformel `max(1, round(dmg·(1−Resistenz)))` (Originalregel) + `HitLedger` gegen doppelte Wertung eines Projektils. Die Arcade-Regeln wurden nicht verändert.
* **Audio** (synthetisiert), **Rekord-/Einstellungs-Speicher**.

Die Quests werden im Einzelspieler mit Asteroiden-/Gegner-/Punkte-/Systemereignissen gefüttert und im Hauptmenü angezeigt. Ob/wie das Spiel dadurch bereichert wird, ist eine Designfrage; die Systeme verändern die Arcade-Mechanik nicht.

## 5. LAN-Architektur

* **Lobby:** Der Host erstellt `LanServer` und verbindet sich über 127.0.0.1 als normaler Client (Host-Rolle nur für diese Loopback-Verbindung – Fix gegen Wettlauf, siehe Test „Host-Rolle gehört dem Server-Ersteller“).
* **Ablauf:** `hello` → `welcome` → `snapshot`-Broadcasts (50 ms) → `start_request` (nur Host; PvP nur mit genau 2 Spielern) → `setup_started` → `ready` → `countdown` (3 s) → `game_started`.
* **PvP (Host-autoritativ):** Client sendet `pvp_input` (alle 50 ms) und `pvp_fire` (Waffe + Sequenznummer). Der Server verwirft doppelte/verspätete Sequenzen, Waffen außerhalb der Spielphase und unmögliche Schussfolgen (Laser < 80 ms, Torpedo < 200 ms) und begrenzt die Warteschlange (16). `PvpWorld` auf dem Host berechnet alles (Bewegung, Treffer, Punkte, Leben, Respawn, Ergebnis) und sendet `pvp_snapshot` (50 ms). Der Client simuliert nichts und rendert aus dem Snapshot (`PvpClientView`).
* **Punktekampf:** Jeder Client simuliert seine eigene Welt; `points_state` (normierte Position, Schiff, Punkte, System) dient nur der Anzeige (Ghosts/Rangliste).
* **Robustheit:** Zeilenlimit 16 384 B, Tiefenlimit im JSON-Parser, Werte werden begrenzt (`Json.Num/Int`), unbekannte Typen ignoriert, ungültiges JSON beendet nur die betreffende Verbindung; Host-Ende ⇒ `server_stopped` an alle; Client-Ende ⇒ Gegner gilt als eliminiert.

## 6. Phasen (durchgeführt)

1. Analyse von Python-Original und Vorgängerport → Befunde oben.
2. Messung der Sprite-Metriken und Referenzwerte mit echtem Pygame.
3. Sim-Schicht: Kern, Entitäten, KI, Hintergrund, Welten, Netzwerk, Speicher, Inventar/Quests.
4. Tests (Golden gegen Python, Spielregeln, LAN über echte Sockets) – Fehler gefunden und behoben (Host-Wettlauf, Pygame-`center`-Rundung, Socket-Shutdown).
5. Unity-Schicht (UI, Rendering, Eingabe, Controller, Audio), Compile-Check gegen API-Nachbildung.
6. Szenen, Prefabs, Metas, Build Settings, Paketliste, ProjectSettings.
7. Dokumentation, Paketierung.

## 7. Noch auszuführen (benötigt Unity)

Import/Kompilierung im Editor, Play-Test aller Szenen, Layout-Feinschliff, echter Zwei-Instanzen-Test mit Unity-Builds. Siehe `PARITY_STATUS.md`.
