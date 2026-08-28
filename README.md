# 🚀 Star Wars – Raumschiff vs. Asteroiden

Ein actiongeladenes **2D-Arcade-Spiel im Star-Wars-Stil**. Steuere dein Raumschiff durch ein gefährliches Asteroidenfeld, zerstöre Hindernisse mit Blastern und Torpedos und versuche, den Highscore zu knacken.

## Features

- Mehrere auswählbare Schiffe (X-Wing, Millennium Falcon, TIE-Fighter, Battle Droid)
- Blaster- und Torpedo-Waffen
- Dynamisch generierte Asteroiden mit Explosionseffekten
- Bildschirmgrößenänderung (resizable window)

## Voraussetzungen

- Python 3.8 oder neuer
- pygame (Spiel-Framework)

Empfohlene Installation (virtuelle Umgebung):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install pygame
```

(Hinweis: Es gibt aktuell keine requirements.txt im Repo; nur pygame ist erforderlich.)

## Starten

Aus dem Projektverzeichnis:

```bash
python StarWarsGame.py
```

Bei Problemen mit Grafiken oder Assets sicherstellen, dass der Ordner `Pixelarts/` im Projekt vorhanden ist.

## ⌨️ Steuerung

| Taste     | Aktion               |
| --------- | -------------------- |
| A / ←     | Nach links bewegen   |
| D / →     | Nach rechts bewegen  |
| W / ↑     | Blaster schießen     |
| S / ↓     | Torpedo schießen     |
| H         | Hitbox ein-/ausblenden |
| 1 / 2 / 3 / 4 | Schneller Schiffswechsel |
| Esc       | Spiel beenden / Zurück |

## Projektstruktur

- `StarWarsGame.py` — Einstiegspunkt des Spiels und Hauptspiel-Loop
- `game/` — Spiel-Logik und UI
  - `game/assets.py` — Lädt Grafiken und setzt das Fenster-Icon
  - `game/entities.py` — Asteroiden, Schiffe, Laser, Torpedos, Explosionen
  - `game/ui/` — Menü-, Auswahl- und Game-Over-Bildschirme
  - `game/background/` — Parallaxe- und Hintergrund-Manager
- `Pixelarts/` — Pixel-Art-Grafiken und Assets (nicht im Paket enthalten)

## Mitwirken

Beiträge sind willkommen. Vorschläge:

- Fehler melden oder Pull Requests für Bugfixes/Verbesserungen
- Weitere Schiffe, Waffen oder Leveldesign hinzufügen

Bitte vor größeren Änderungen ein Issue öffnen, um die Idee kurz zu besprechen.

## Lizenz & Hinweis zu Inhalten

Dieses Projekt ist zu Lern- und Demonstrationszwecken. Alle Star-Wars-bezogenen Inhalte und Marken liegen bei ihren jeweiligen Rechteinhabern. Falls Assets aus fremden Quellen verwendet werden, bitte die jeweiligen Lizenzbedingungen beachten.

---

<p align="center"><em>“Sir, the possibility of successfully navigating an asteroid field is approximately<br>three thousand seven hundred and twenty to one!”</em><br>— C-3PO</p>
