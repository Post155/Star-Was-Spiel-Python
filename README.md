# Star Wars – Unity-Port (C#)

Port des Pygame-Spiels „Star-Was-Spiel“ nach Unity. Die Spiellogik des Originals steckt in einer **Unity-unabhängigen C#-Bibliothek** (`Assets/Scripts/Sim`), die automatisiert gegen den echten Python-Code getestet wurde. Die Unity-Schicht (`Assets/Scripts/Game`) stellt Menüs, Darstellung, Eingabe und Audio bereit.

> **Wichtig – Teststatus:** Eine Unity-Installation stand bei der Erstellung nicht zur Verfügung. Die Simulations-, Netzwerk-, Speicher- und Inventarlogik ist real kompiliert und getestet (179 Tests, siehe `TEST_REPORT.md`). Die Unity-Schicht, die Szenen und die Prefabs wurden **nicht in Unity ausgeführt**; die Unity-Schicht wurde nur gegen eine selbstgeschriebene API-Nachbildung kompiliert. Details und offene Punkte: `PARITY_STATUS.md`.

## Schnellstart

1. Unity **6000.6.6f1** (wie in `ProjectSettings/ProjectVersion.txt`) öffnen → Projektordner wählen. Der Package Manager löst `com.unity.ugui 2.0.0` neu auf (Internet nötig).
2. Szene `Assets/Scenes/MainMenu.unity` öffnen und **Play** drücken. (Jede der 10 Szenen startet für sich; ein unbekannter Szenenname führt automatisch ins Hauptmenü.)
3. Falls Unity beim ersten Import eine Datei beanstandet oder die Pixelarts unscharf wirken: Menü **Star Wars → 1) Alles einrichten**. Das stellt Import-Einstellungen, Szenen, Build Settings, Prefabs und ScriptableObjects wiederholbar her.
4. Tests: **Window → General → Test Runner → EditMode → Run All** oder ohne Unity:
   `dotnet run --project Tests/ConsoleRunner -- Tests/Golden/golden.json`

Details: `UNITY_SETUP.md`.

## Spielmodi

| Modus | Beschreibung |
|---|---|
| Einzelspieler | Fraktion → Schwierigkeit → Schiff → Spiel. Asteroiden, KI-Gegner ab 2000/5000/10000 Punkten, Sternensysteme, Rekord (Highscore). |
| Lokal: Punktekampf | Zwei **getrennte** Spielwelten nebeneinander (je 400×600), 3 Minuten, TAB = Rangliste, Ghost des Gegners als halbtransparentes Schiff. |
| Lokal: Letzter Überlebender | Direktes Duell auf einer Fläche (Spieler 1 unten, Spieler 2 oben). |
| LAN: Punktekampf | Bis 10 Spieler, jeder in seiner eigenen Welt, Ghosts + Live-Rangliste. |
| LAN: Letzter Überlebender | 2 Spieler, **Host-autoritative** Simulation, Client sendet nur Eingaben. |

## Steuerung

| Aktion | Einzelspieler / LAN | Lokal Spieler 1 | Lokal Spieler 2 |
|---|---|---|---|
| Bewegen | A/D oder ←/→ | A / D | ← / → |
| Laser | Leertaste, W oder ↑ | W | ↑ |
| Torpedo (nur X-Wing, TIE) | S oder ↓ | S | ↓ |

Weitere Tasten: **H** Hitboxen (Debug), **1–4** Schiff wechseln (nur Einzelspieler, Debug), **TAB** Rangliste (gedrückt halten), **Esc** zurück/Menü, **R** Neustart nach Game Over. Menüs: Maus oder Zifferntasten wie angezeigt.

## LAN-Spiel

* Host: *Mehrspieler → LAN → Regel wählen → Host erstellen*. Die Lobby zeigt die IP-Adressen des Hosts und den Port **48732** (TCP; in der Firewall freigeben).
* Mitspieler: gleiche Regel wählen, Host-IP eintragen → *Beitreten*. Der Host startet, danach wählt jeder Fraktion/Schiff, nach „bereit“ läuft ein 3-s-Countdown.
* Zwei Instanzen auf einem PC: ein Build + der Editor, IP `127.0.0.1`. „Run In Background“ ist aktiviert, damit der Host auch ohne Fokus weiterläuft.
* Kein externer Server und keine Internetverbindung nötig.

## Projektstruktur

```
Assets/
  Scenes/                 10 Szenen (Kamera + SceneBootstrap)
  Resources/Pixelarts/    Original-Grafiken (Sprite-Import: Point, PPU 1, unkomprimiert)
  Resources/Prefabs/      19 Pool-Prefabs (SpriteRenderer-Vorlagen)
  Scripts/Sim/            reine C#-Logik (asmdef ohne Engine-Referenzen)
      Core, Data, Entities, Enemies, Background, World, Net, Save, Systems
  Scripts/Game/           Unity-Schicht: Menüs, Controller, Rendering, UI, Audio, Eingabe
  Scripts/Editor/         Menü „Star Wars“ (Einrichtung/Reparatur)
  Tests/EditMode/         NUnit-Wrapper + gemeinsame Testsuite
Tests/ConsoleRunner/      Testlauf ohne Unity
Tests/Golden/golden.json  Referenzwerte aus dem Original-Python
Tools/                    Python-Werkzeuge (Datengenerierung)
```

## Dokumentation

`MIGRATION_PLAN.md` · `FILE_BY_FILE_MIGRATION.md` · `UNITY_SETUP.md` · `TEST_REPORT.md` · `PARITY_STATUS.md`
