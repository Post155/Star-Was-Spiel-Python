# Testbericht

Stand der Erstellung: Oktober 2026. **Alle Angaben unten sind tatsächlich ausgeführte Läufe**; alles, was nicht ausgeführt werden konnte, ist ausdrücklich als solches aufgeführt.

## 1. Umgebung

* Linux-Container, .NET SDK 8.0.131, C# `LangVersion 9`, Ziel `netstandard2.1` (Sim-Assembly) bzw. `net8.0` (Testprogramm).
* Python 3.12 + **Pygame 2.6.1** (headless) zum Messen der Sprites und zum Erzeugen der Referenzwerte aus dem **originalen Python-Code**.
* **Kein Unity-Editor** verfügbar.

## 2. Ausgeführte Prüfungen

| Prüfung | Befehl / Methode | Ergebnis |
|---|---|---|
| Kompilierung `StarWars.Sim` (27 Dateien, ca. 3 900 Zeilen) | `dotnet build` (netstandard2.1, C# 9) | 0 Fehler, 0 Warnungen |
| Testsuite (Konsole) | `dotnet run --project Tests/ConsoleRunner -- Tests/Golden/golden.json` | **179 bestanden, 0 fehlgeschlagen** (mehrfach wiederholt, stabil) |
| Kompilierung `Scripts/Game` (13 Dateien) | gegen **selbstgeschriebene** UnityEngine-/uGUI-Nachbildung | 0 Fehler. *Aussagekraft begrenzt:* prüft Syntax und Typen gegen meine Annahmen über die API, nicht gegen echtes Unity. |
| Kompilierung `Scripts/Editor` | gegen selbstgeschriebene UnityEditor-Nachbildung | 0 Fehler (gleiche Einschränkung) |
| Kompilierung `Assets/Tests/EditMode/SimSuiteTests.cs` | gegen die **echte** `nunit.framework.dll` aus dem Unity-Paket des Projekts | 0 Fehler |
| Szenen/Prefabs/Build Settings | YAML-Parser + Prüfung aller `fileID`-Verweise | 10 Szenen, 19 Prefabs, EditorBuildSettings: 0 Fehler. *Nicht von Unity geladen.* |
| Metadateien | Skript | 139 `.meta`, keine doppelten GUIDs, keine Datei ohne `.meta` |

### Nicht ausgeführt (benötigt Unity)

* Import und Kompilierung des Projekts im Editor (also auch keine Unity-Compiler-Logs).
* Start/Play aller Szenen, Klicktests der Buttons, Layout bei verschiedenen Auflösungen, Rendering/Sortierung, Audio, Fenster-Resize.
* Laden der handgeschriebenen Szenen-/Prefab-YAMLs durch Unity.
* LAN zwischen **zwei Unity-Prozessen** (getestet wurde mit echten TCP-Sockets über Loopback in einem Prozess, siehe unten).
* Unity Test Runner (der Wrapper ist kompiliert, aber nicht im Editor gelaufen).

## 3. Ergebnis je Testgruppe

| Gruppe | bestanden | fehlgeschlagen |
|---|---|---|
| Golden: EnemyManager (Schwierigkeit/Skalierung/Spawn/Balancing) vs. Python | 1 | 0 |
| Golden: EnemyMovement (Steuerung) vs. Python | 8 | 0 |
| Golden: Spielerschiffe (Position, Alpha-Hitbox, Laser, Torpedo) vs. Python | 16 | 0 |
| Golden: Asteroiden (Größe, Punkte) vs. Python | 2 | 0 |
| Spielerschiff: Bewegung, Grenzen, Leben, Unverwundbarkeit | 11 | 0 |
| Asteroiden und Schwierigkeitsprofile | 8 | 0 |
| Gegner: Freischaltung, Warnungen, Spawn, Schaden | 13 | 0 |
| Sternensysteme, Hintergrund, Systemwechsel | 13 | 0 |
| Einzelspieler-Simulation (Ablauf wie run_game_session) | 7 | 0 |
| Lokaler Punktekampf: zwei vollständig getrennte Welten | 7 | 0 |
| PvP-Duell (Letzter Überlebender / Punktekampf-Regel): Host-autoritative Welt | 15 | 0 |
| JSON-Parser/-Writer | 11 | 0 |
| Speichersystem | 9 | 0 |
| Inventar & Items | 8 | 0 |
| Questsystem | 8 | 0 |
| LAN: Host erstellen, per IP beitreten, Lobby-Zustand (echte Sockets) | 16 | 0 |
| LAN-PvP: Host-autoritative Simulation, Eingaben, Schüsse, Snapshots (2 Instanzen) | 11 | 0 |
| LAN: Verbindungsabbruch des Clients während des Spiels | 2 | 0 |
| LAN: Host beendet das Spiel | 1 | 0 |
| LAN-Punktekampf: bis zu 10 Spieler, Ghost-Daten, Rangliste | 7 | 0 |
| LAN: fehlerhafte und unzulässige Nachrichten | 5 | 0 |

## 4. Abgleich mit dem Original (Golden-Tests)

Referenzwerte stammen aus dem **ausgeführten Original-Code** (`Tests/Golden/golden.json`, erzeugt mit `Tools/gen_golden.py`):

* `EnemyManager`: Schwierigkeitsskalierung, Maximalzahl, Spawn-Intervall, Freischalt-Tier und alle balancierten Archetyp-Werte für 4 Schwierigkeiten × 6 Systeme × 13 Punktestände – **312 Kombinationen identisch**.
* `EnemyMovement`: Trajektorien (160 Ticks) für alle 4 Archetypen – identisch (Toleranz 1e-9).
* Spielerschiffe: Position, Alpha-Hitbox, Laser- und Torpedo-Rechtecke für 4 Schiffe in 3 Positionen – identisch. (Dabei wurde die Pygame-Rundung von `get_rect(center=…)` entdeckt und korrigiert.)
* Asteroiden: Skalen, Pixelgrößen, Punktwerte – 160 Stichproben identisch.

## 5. Testmatrix (Anforderung → Status)

| Test | Erwartetes Ergebnis | Status |
|---|---|---|
| Start des Spiels | Hauptmenü erscheint | **nicht ausgeführt** (Unity) |
| Auswahl einer Fraktion | Auswahl wird übernommen | **nicht ausgeführt** (Menülogik in `AppState`, Unity-abhängig) |
| Auswahl der Schwierigkeit | richtige Konfiguration | Konfiguration getestet (Golden + Profile); Menü nicht ausgeführt |
| Auswahl eines Schiffs | richtiges Schiff | Schiffskatalog getestet; Menü/Darstellung nicht ausgeführt |
| Spielerbewegung | innerhalb der Grenzen | **getestet** (Sim) |
| Laser | richtige Position | **getestet** (Golden) |
| Torpedos | Waffe/Schaden | **getestet** (Golden + Schadensformel) |
| Asteroiden | Spawn, Kollision, Punkte | **getestet** (Sim) |
| Gegner | KI, Bewegung, Angriffe | **getestet** (Bewegung Golden; Zielverfolgung, Salven) |
| Gegnerfreischaltung | Schwellen + Warnungen | **getestet** |
| Systemwechsel | Hintergrund/Info ändern sich | Logik **getestet** (30 s, 2000 Punkte, Planetenfenster); Darstellung nicht ausgeführt |
| Tod und Neustart | Zustand zurückgesetzt | Tod **getestet**; Neustart (Szene laden) nicht ausgeführt |
| Highscore | Bestwert gespeichert | **getestet** (Speicherdienst); Dialog nicht ausgeführt |
| Punktekampf | zwei getrennte Simulationen | **getestet** (Sim); Anzeige nicht ausgeführt |
| Letzter Überlebender | PvP-Regeln, Gewinner | **getestet** (Sim) |
| LAN-Host | Lobby und Start | **getestet** (echte Sockets) |
| LAN-Client | Verbindung/Zustand | **getestet** (echte Sockets) |
| LAN-PvP | Bewegung/Schüsse/Treffer synchron | **getestet** auf Treiberebene (Host-Welt + Client-Ansicht über TCP); nicht mit zwei Unity-Prozessen |
| Verbindungsabbruch | kontrolliert | **getestet** (Client weg, Host weg, Müll/Übergröße/falsche Version) |
| Speicherung | speichern/laden | **getestet** (inkl. beschädigt/älter/neuer/ungültige Werte) |
| Inventar | Hinzufügen/Entfernen/Stapel | **getestet** |
| Quests | Fortschritt/Abschluss/Belohnung | **getestet** |

## 6. Gefundene und behobene Fehler während der Tests

1. **Host-Wettlauf:** Der zuerst verbundene Client wurde Host; bei gleichzeitigem Start konnte das ein Mitspieler sein. → Host-Rolle nur für die Loopback-Verbindung des Server-Erstellers (neuer Test).
2. **Pygame-Rundung:** `get_rect(center=…)` rundet; Torpedo-Rechteck des TIE war um 1 px falsch. → `RectI.FromCenter`.
3. **Trennung nicht sofort erkannt:** `Close()` während ein anderer Thread liest sendete kein FIN. → `Socket.Shutdown` vor `Close`.

## 7. Offene Punkte

Siehe `PARITY_STATUS.md` („Offen / Risiken“).

## 8. Vollständiges Testprotokoll (letzter Lauf)

## Golden: EnemyManager (Schwierigkeit/Skalierung/Spawn/Balancing) vs. Python
- PASS  312 Kombinationen (4 Schwierigkeiten x 6 Systeme x 13 Punktestände x 4 Archetypen) stimmen exakt

## Golden: EnemyMovement (Steuerung) vs. Python
- PASS  EnemyMovement[standard] Referenzdaten vorhanden
- PASS  EnemyMovement[fast] Referenzdaten vorhanden
- PASS  EnemyMovement[heavy] Referenzdaten vorhanden
- PASS  EnemyMovement[elite] Referenzdaten vorhanden
- PASS  EnemyMovement[standard]: 160 Ticks Trajektorie identisch zu Python (Toleranz 1e-9)
- PASS  EnemyMovement[fast]: 160 Ticks Trajektorie identisch zu Python (Toleranz 1e-9)
- PASS  EnemyMovement[heavy]: 160 Ticks Trajektorie identisch zu Python (Toleranz 1e-9)
- PASS  EnemyMovement[elite]: 160 Ticks Trajektorie identisch zu Python (Toleranz 1e-9)

## Golden: Spielerschiffe (Position, Alpha-Hitbox, Laser, Torpedo) vs. Python
- PASS  xwing (links x0) stimmt mit Python überein
- PASS  xwing (links x-1) stimmt mit Python überein
- PASS  xwing (links x7) stimmt mit Python überein
- PASS  xwing (links x-1) stimmt mit Python überein
- PASS  milleniumfalcon (links x0) stimmt mit Python überein
- PASS  milleniumfalcon (links x-1) stimmt mit Python überein
- PASS  milleniumfalcon (links x7) stimmt mit Python überein
- PASS  milleniumfalcon (links x-1) stimmt mit Python überein
- PASS  tiefighter (links x0) stimmt mit Python überein
- PASS  tiefighter (links x-1) stimmt mit Python überein
- PASS  tiefighter (links x7) stimmt mit Python überein
- PASS  tiefighter (links x-1) stimmt mit Python überein
- PASS  battledroid (links x0) stimmt mit Python überein
- PASS  battledroid (links x-1) stimmt mit Python überein
- PASS  battledroid (links x7) stimmt mit Python überein
- PASS  battledroid (links x-1) stimmt mit Python überein

## Golden: Asteroiden (Größe, Punkte) vs. Python
- PASS  160 Asteroiden: Punktwert und Pixelgröße identisch
- PASS  Asteroid-Skalen stammen aus {0.25,0.5,0.75,1.0}

## Spielerschiff: Bewegung, Grenzen, Leben, Unverwundbarkeit
- PASS  Startposition mittig unten
- PASS  linke Bildschirmgrenze
- PASS  rechte Bildschirmgrenze
- PASS  3 Leben
- PASS  erster Treffer: 2 Leben, nicht tot
- PASS  während der Unverwundbarkeit kein Schaden
- PASS  nach 2 s wieder verwundbar
- PASS  dritter Treffer zerstört das Schiff
- PASS  Torpedo nur X-Wing/TIE
- PASS  Geschwindigkeiten 12/14/11/12
- PASS  Gegnerschiffe laut Regel (XWing->TIE, Falcon->Droid, TIE->XWing, Droid->Falcon)

## Asteroiden und Schwierigkeitsprofile
- PASS  Experte: Parameter wie constants.py
- PASS  vier Stufen
- PASS  unbekannte Stufe -> normal
- PASS  Asteroid startet oberhalb des Bildschirms
- PASS  Fallgeschwindigkeit = speed * Multiplikator
- PASS  Geschwindigkeitsbereich 2..8 * Multiplikator
- PASS  Animation: Frame wechselt alle 5 Ticks
- PASS  Kollisionsrechteck = 70 % zentriert

## Gegner: Freischaltung, Warnungen, Spawn, Schaden
- PASS  unter 2000 Punkten: keine Gegner, keine Warnung
- PASS  bei 2000 Punkten erscheint die Warnung (Tier 1)
- PASS  während der Warnung spawnt kein Gegner
- PASS  nach der Warnung (2,5 s) spawnen Gegner
- PASS  Gegner ist TIE-Fighter-Modell gegen X-Wing
- PASS  5000 Punkte: Warnung Tier 2
- PASS  10000 Punkte: Elite-Warnung (alle Stufen werden nacheinander gewarnt)
- PASS  Schwerer Gegner: Rüstung (28 %) -> min. 1 Schaden
- PASS  Torpedo (4 Schaden) auf Standard-Gegner
- PASS  Rüstungsformel max(1, round(dmg*(1-res)))
- PASS  Rüstung Torpedo gegen Schwer: round(4*0.72)=3
- PASS  KI folgt dem Spieler horizontal (Zielverfolgung)
- PASS  Gegner feuert Laser-Salven (und ggf. Torpedos) auf den Spieler

## Sternensysteme, Hintergrund, Systemwechsel
- PASS  12 Systeme, EARTH zuerst
- PASS  jedes System genau einmal
- PASS  Reihenfolge ist zufällig (zwei Seeds unterscheiden sich)
- PASS  BLACKHOLE/TODESSTERN/STERNZERSTÖRER ohne eigenen Planetenschlüssel (Original-Verhalten)
- PASS  Planetenpool-Fallback umfasst 13 Bilder
- PASS  Asteroiden-Tempo je System (EARTH 0.5, BLACKHOLE 2.5)
- PASS  Systembonus (0, .15, .30, .50, danach .50)
- PASS  Sterne: Layer1 >= 50, Layer2 >= 20
- PASS  vor 30 s noch kein Wechsel
- PASS  nach 30 s startet die Karten-Überblendung
- PASS  nach 5 s ist das System gewechselt
- PASS  2000 Punkte lösen den Wechsel aus
- PASS  Planet erscheint erst nach 10 s Eintrittsverzögerung, nur einer pro System

## Einzelspieler-Simulation (Ablauf wie run_game_session)
- PASS  Asteroiden entstehen und werden abgeschossen, Punkte steigen
- PASS  Spieler bleibt innerhalb der Bildschirmgrenzen
- PASS  Punkte entsprechen Summe der Asteroidenpunkte (keine Doppelwertung)
- PASS  Ohne Eingabe stirbt der Spieler irgendwann (Tod nur einmal gemeldet)
- PASS  Nach dem Tod keine Aktionen mehr
- PASS  Debug-Schiffswechsel leert Projektile und ersetzt das Schiff
- PASS  Simulation ist bei gleichem Seed deterministisch

## Lokaler Punktekampf: zwei vollständig getrennte Welten
- PASS  zwei unterschiedliche Weltinstanzen mit eigenen Listen
- PASS  Eingaben wirken nur in der eigenen Welt (P2 schoss nie)
- PASS  Spieler 2 nutzt TIE (Torpedo-fähig), Spieler 1 X-Wing
- PASS  Welt 400x600 je Spieler
- PASS  Match endet nach 180 s oder wenn beide tot sind
- PASS  Rangliste sortiert absteigend
- PASS  Gleichstand -> kein Sieger

## PvP-Duell (Letzter Überlebender / Punktekampf-Regel): Host-autoritative Welt
- PASS  Host unten, Gegner oben
- PASS  PvP-Geschwindigkeit 12 für alle
- PASS  Treffer: Schaden 1, Leben -1, Angreifer erhält 150 Punkte
- PASS  Treffer registriert genau einmal pro Projektil
- PASS  Getroffener Spieler respawnt verzögert und ist danach unverwundbar
- PASS  Match endet, wenn ein Spieler eliminiert ist (Sieger = Überlebender)
- PASS  Kill-Bonus 1000 vergeben
- PASS  Eliminierter Spieler kann nicht mehr schießen
- PASS  Ergebnis bleibt nach Spielende stabil
- PASS  Punktekampf-Regel: endet nach 180 s
- PASS  Gleichstand 0:0 -> Unentschieden (winner_id null)
- PASS  Verbindungsabbruch des Gegners: Host gewinnt
- PASS  Asteroiden: Obergrenze 36, kein Leck durch seitlich verlassende Asteroiden
- PASS  Snapshot ist gültiges JSON im Original-Format (version 1)
- PASS  Client-Ansicht übernimmt Spieler und Systemreihenfolge

## JSON-Parser/-Writer
- PASS  Roundtrip erhält Typen und Sonderzeichen
- PASS  fehlerhaftes JSON wird abgelehnt: {
- PASS  fehlerhaftes JSON wird abgelehnt: {"a":}
- PASS  fehlerhaftes JSON wird abgelehnt: [1,2
- PASS  fehlerhaftes JSON wird abgelehnt: {"a" 1}
- PASS  fehlerhaftes JSON wird abgelehnt: nope
- PASS  fehlerhaftes JSON wird abgelehnt: {"a":"x}
- PASS  fehlerhaftes JSON wird abgelehnt: {"a":1} x
- PASS  Zahlenformate
- PASS  Json.Int begrenzt
- PASS  Tief verschachteltes JSON wird abgewiesen

## Speichersystem
- PASS  erster Start: leer
- PASS  neuer Rekord wird erkannt und gespeichert
- PASS  Laden: Highscore + Einstellungen
- PASS  beschädigte Datei: Wiederherstellung aus Backup
- PASS  beschädigt ohne Backup: sauberer Neustart, keine Ausnahme
- PASS  Import des alten Python-Highscores {"highscore": 6025}
- PASS  Datei aus neuerer Version wird nicht fehlinterpretiert
- PASS  ältere Datei ohne Version wird migriert
- PASS  ungültige Werte werden auf sichere Standardwerte begrenzt

## Inventar & Items
- PASS  Hinzufügen (Repair-Kit, Stapel 5)
- PASS  Stapelregel: 7 Kits = 2 Slots (5+2)
- PASS  nicht stapelbar: Schildverstärker belegt eigenen Slot
- PASS  Kapazitätsgrenze: Rest wird zurückgegeben
- PASS  unbekanntes Item wird abgewiesen
- PASS  Entfernen nur ganz oder gar nicht
- PASS  Änderungsereignis wird ausgelöst
- PASS  Serialisierung erhält Bestand

## Questsystem
- PASS  nicht angenommene Quests sammeln keinen Fortschritt
- PASS  Annahme
- PASS  Fortschritt 4/10
- PASS  Abschluss bei Erreichen des Ziels (genau einmal gemeldet)
- PASS  Belohnung wird abgeholt
- PASS  Belohnung nicht doppelt abholbar
- PASS  volles Inventar: Quest bleibt abholbar
- PASS  Queststatus wird gespeichert/geladen (inkl. 'Belohnung bereits beansprucht')

## LAN: Host erstellen, per IP beitreten, Lobby-Zustand (echte Sockets)
- PASS  Host und Client verbunden, beide sehen 2 Spieler
- PASS  eindeutige Spieler-IDs, Host korrekt erkannt
- PASS  Namen werden synchronisiert
- PASS  Nur der Host darf starten (Client-Start wird ignoriert)
- PASS  Host-Start -> beide Clients wechseln in die Setup-Phase
- PASS  Countdown startet erst, wenn ALLE bereit sind
- PASS  alle bereit -> Countdown (3 s) bei beiden
- PASS  Countdown-Restzeit ist uhrenunabhängig (remaining_ms) und <= 3000 ms
- PASS  Countdown endet -> Spielphase bei beiden
- PASS  Schiffswahl wurde übertragen
- PASS  Beitritt nach Spielstart wird abgelehnt
- PASS  Host-Rolle gehört dem Server-Ersteller, auch wenn ein Mitspieler früher verbindet
- PASS  falscher Spielmodus wird mit Fehlermeldung abgelehnt
- PASS  PvP: dritter Spieler wird abgelehnt (max. 2)
- PASS  PvP-Start mit nur einem Spieler wird verhindert
- PASS  Verbindungsfehler (kein Server) wird sauber gemeldet

## LAN-PvP: Host-autoritative Simulation, Eingaben, Schüsse, Snapshots (2 Instanzen)
- PASS  beide Instanzen in der Spielphase
- PASS  Host-Welt: Host unten (xwing), Client oben (tiefighter)
- PASS  Host-Eingabe bewegt Host-Schiff nach rechts
- PASS  Client-Eingabe (über TCP) bewegt Client-Schiff in der Host-Welt nach links
- PASS  Client-Schuss kam beim Host an und wurde gezählt (Server-seitig validiert)
- PASS  Host sendet Snapshots
- PASS  Client wendet Snapshots auf seine Ansicht an
- PASS  Client sieht Host-Position wie in der autoritativen Welt (±15 px)
- PASS  Client sieht eigenes Schiff oben (role=top) und Punkte/Leben vom Host
- PASS  Client sieht Projektile/Asteroiden-Listen aus dem Snapshot
- PASS  Systemreihenfolge des Hosts wurde beim Client übernommen

## LAN: Verbindungsabbruch des Clients während des Spiels
- PASS  Host erkennt die Trennung und beendet das Match kontrolliert
- PASS  getrennter Spieler gilt als eliminiert

## LAN: Host beendet das Spiel
- PASS  Client erkennt Host-Abbruch (server_stopped)

## LAN-Punktekampf: bis zu 10 Spieler, Ghost-Daten, Rangliste
- PASS  3 Spieler in der Lobby
- PASS  Countdown und Start für alle drei
- PASS  Host sieht Ghosts beider Clients mit Punkten und System
- PASS  Rangliste ist nach Punkten sortiert (4200 > 900 > ...)
- PASS  Ghost-Position normiert (0..1), Schiff übertragen
- PASS  Ghosts sind reine Anzeige: keine Auswirkung auf die lokale Simulation
- PASS  Verlassen eines Spielers wird erkannt (Ghost verschwindet)

## LAN: fehlerhafte und unzulässige Nachrichten
- PASS  Müll statt JSON beendet nur diese Verbindung, Server läuft weiter
- PASS  Überlange Nachricht wird verworfen (Verbindung beendet)
- PASS  falsche Protokollversion -> Fehlermeldung
- PASS  Werte werden geprüft/begrenzt (x<=1, y>=0, Score>=0)
- PASS  unbekannte Nachrichtentypen werden ignoriert

