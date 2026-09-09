# 🚀 Star Wars – KI-Raumschiffkampf

Ein 2D-Arcade-Spiel im Star-Wars-Stil mit vier spielbaren Schiffen und einem modularen KI-Gegnersystem.

## Features

- Spielbare Schiffe: X-Wing, Millennium Falcon, TIE-Fighter und Battle Droid
- Feste Gegenschiff-Regel:
  - X-Wing → TIE-Fighter
  - Millennium Falcon → Battle Droid
  - TIE-Fighter → X-Wing
  - Battle Droid → Millennium Falcon
- Vier KI-Typen: Standard, Schnell, Schwer und Elite
- Gegner verfolgen, flankieren, unterstützen und weichen Laser-/Torpedobahnen aus
- Zielorientierte Lasersalven und taktische Torpedos
- Dynamische Schwierigkeit über Punktzahl und aktuelles Sternsystem
- Eigene Gegner-Hitboxen, HP-Balken, Trefferblitz, Explosion und Punktebonus
- Mehrere Gegner gleichzeitig mit Spawn-Abstand und Gruppenrollen
- Resizable Window und bestehendes Hintergrund-/Sternsystem

## Voraussetzungen

- Python 3.8 oder neuer
- pygame oder pygame-ce

```bash
python -m pip install pygame
```

Alternativ mit pygame-ce:

```bash
python -m pip install pygame-ce
```

## Starten

```bash
python StarWarsGame.py
```

## Steuerung

| Taste | Aktion |
| --- | --- |
| A / ← | Nach links bewegen |
| D / → | Nach rechts bewegen |
| W / ↑ / Leertaste | Laser schießen |
| S / ↓ | Torpedo schießen (wenn Schiff Torpedos besitzt) |
| H | Hitboxen ein-/ausblenden |
| 1 / 2 / 3 / 4 | Debug-Schnellwechsel des Spielerschiffs |
| Esc | Runde beenden / zurück |

## Neue KI-Struktur

```text
game/enemies/
├── __init__.py       # Öffentliche API
├── base.py           # EnemyBase, HP, Hitbox, Trefferstatus
├── ai.py             # Entscheidungen, Reaktionszeit, Dodge, Gruppenrollen
├── movement.py       # Weiches Steering / Bewegung
├── weapons.py        # Lasersalven und taktische Torpedos
├── projectiles.py    # Gegner-Laser und Gegner-Torpedos
├── manager.py        # Spawn, Schwierigkeit, Kollision, Score, Lifecycle
├── config.py         # Archetypen + Gegenschiff-Zuordnung
└── audio.py          # Sicherer Explosion-Sound
```

Die Trennung ist absichtlich auf spätere Bossgegner, Begleitjäger, Fraktionen, Spezialwaffen, Koop und Wellenmodus vorbereitet.

## Balancing

Die wichtigsten Werte stehen zentral in `game/enemies/config.py`. Dort können HP, Geschwindigkeit, Reaktionszeit, Ausweichchance, Feuerfrequenz, Schaden, Torpedo-Cooldown und Punktewerte je Gegnerklasse angepasst werden.

Spawnrate und maximale Gegnerzahl werden in `game/enemies/manager.py` aus Score + Systemschwierigkeit berechnet.

## Hinweis

Dieses Projekt ist zu Lern- und Demonstrationszwecken. Star-Wars-Marken und fremde Assets unterliegen den Rechten ihrer jeweiligen Eigentümer.
