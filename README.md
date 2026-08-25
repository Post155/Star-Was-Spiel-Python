# Star Wars Spiel

Dieses Projekt ist ein kleines Pygame-Spiel mit Sternen, Asteroiden und Raumschiff-Auswahl.

## Struktur

- `StarWarsGame.py` — Einstiegspunkt des Spiels und Hauptspiel-Loop
- `game/assets.py` — Lädt alle Bilder aus `Pixelarts/`
- `game/entities.py` — Spielobjekte wie Asteroiden, Laser, Explosionen und Schiffe
- `game/ui.py` — Menüs und Bildschirme wie Schiffsauswahl und Game Over
- `game/constants.py` — zentrale Konstanten wie Auflösung, Farbcodes und Asset-Pfade
- `Pixelarts/` — alle Grafiken des Spiels

## Starten

```bash
python StarWarsGame.py
```

## Steuerung

- A / D oder Links / Rechts: Schiff bewegen
- Leertaste / W / Hoch: Schießen
- S / Runter: Torpedo
- H: Hitbox ein-/ausblenden
- Escape: Spiel beenden
