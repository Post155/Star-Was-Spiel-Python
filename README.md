# 🚀 Star Wars: Galactic Assault

Ein actionreiches 2D-Arcade-Weltraumspiel im Stil klassischer Star-Wars-Raumschlachten.

Übernimm die Kontrolle über ikonische Raumschiffe, durchquere gefährliche Asteroidenfelder und stelle dich intelligenten KI-Gegnern. Mit jedem erreichten Sternensystem steigt die Herausforderung, während neue Gegner und Bedrohungen freigeschaltet werden.

---

# 🎮 Features

## Spielbare Schiffe

- X-Wing
- Millennium Falcon
- TIE-Fighter
- Battle Droid Fighter

Jedes Schiff verfügt über eigene Eigenschaften, Waffen und Flugcharakteristiken.

---

## Gegner-KI

Vier verschiedene Gegnerklassen:

- Standard
- Schnell
- Schwer
- Elite

Die KI kann:

- Spieler aktiv verfolgen
- Flankierungsmanöver ausführen
- Andere Gegner unterstützen
- Laser- und Torpedoangriffen ausweichen
- Zielgenaue Lasersalven abfeuern
- Taktische Torpedos einsetzen
- Dynamisch auf Spielsituationen reagieren

---

## Gegnerzuordnung

Jedes Spielerschiff besitzt einen fest definierten Gegenspieler:

| Spielerschiff | Gegner |
|--------------|---------|
| X-Wing | TIE-Fighter |
| Millennium Falcon | Battle Droid Fighter |
| TIE-Fighter | X-Wing |
| Battle Droid Fighter | Millennium Falcon |

---

## Asteroidensystem

- Mehrere Asteroidengrößen
- Individuelle Geschwindigkeiten
- Dynamische Spawnraten
- Steigende Asteroidendichte
- Kollisions- und Schadenssystem
- Fortschrittsabhängige Skalierung

---

# ⚙️ Schwierigkeitssystem

Zu Beginn jeder Spielrunde kann eine Schwierigkeitsstufe ausgewählt werden.

## Verfügbare Schwierigkeitsstufen

| Schwierigkeit | Beschreibung |
|--------------|-------------|
| Einfach | Ideal für Einsteiger |
| Normal | Ausgewogenes Standard-Erlebnis |
| Schwer | Höhere Herausforderung durch aggressivere Gegner |
| Experte | Maximale Schwierigkeit für erfahrene Spieler |

## Beeinflusste Werte

Die gewählte Schwierigkeit wirkt sich auf folgende Systeme aus:

- Gegnerische Trefferquote
- Gegner-Lebenspunkte
- Gegnergeschwindigkeit
- Gegner-Aggressivität
- Verfolgungsverhalten
- Gegner-Spawnrate
- Maximale Anzahl aktiver Gegner
- Asteroidendichte
- Asteroidengeschwindigkeit
- Asteroidengröße

---

# 📈 Progression-System

Gegner erscheinen nicht sofort zu Spielbeginn.

Zu Beginn befindet sich der Spieler allein im Sternensystem und kämpft ausschließlich gegen Asteroiden. Dadurch können Steuerung und Waffen zunächst ohne Druck erlernt werden.

## Gegner-Freischaltung

```text
0 - 999 Punkte
└─ Nur Asteroiden

1.000 Punkte
└─ Erste feindliche Schiffe erscheinen

3.000 Punkte
└─ Erweiterte Gegnerklassen werden freigeschaltet

6.000 Punkte
└─ Elite-Gegner erscheinen
```

Vor jeder neuen Gegnerstufe wird eine Warnmeldung angezeigt.

### Beispielmeldungen

```text
⚠ Feindliche Schiffe wurden entdeckt!

⚠ Verstärkte Aktivitäten im System festgestellt!

⚠ Elite-Einheit im Anflug!

⚠ Unbekanntes Signal erkannt!
```

---

# 🌌 Dynamische Sternensysteme

Zusätzlich zur gewählten Schwierigkeit erhöht jedes neue Sternensystem die Gesamtgefahr.

| Sternensystem | Schwierigkeitsbonus |
|--------------|-------------------:|
| System 1 | +0 % |
| System 2 | +15 % |
| System 3 | +30 % |
| System 4 | +50 % |

Die Skalierung beeinflusst:

- Gegnerstärke
- Gegnerverhalten
- Spawnraten
- Asteroidendichte
- Asteroidengeschwindigkeit

Dadurch bleibt das Spiel langfristig herausfordernd, ohne den Spieler zu überfordern.

---

# 🎯 Spielziel

Überlebe möglichst lange und erreiche die höchste Punktzahl.

Der Spieler muss:

- Asteroiden zerstören
- Feindliche Schiffe besiegen
- Torpedos ausweichen
- Sternensysteme durchqueren
- Hohe Punktzahlen erzielen
- Immer stärkere Bedrohungen überleben

Je weiter der Spieler fortschreitet, desto schwieriger werden die Gefechte.

---

# 🎮 Steuerung

| Taste | Aktion |
|--------|--------|
| A / ← | Nach links bewegen |
| D / → | Nach rechts bewegen |
| W / ↑ | Nach oben bewegen |
| Leertaste | Laser schießen |
| S / ↓ | Torpedo abfeuern |
| H | Hitboxen anzeigen |
| 1 / 2 / 3 / 4 | Schiff wechseln (Debug) |
| ESC | Pause / Zurück |

---

# 📦 Installation

## Voraussetzungen

- Python 3.8 oder neuer
- pygame oder pygame-ce

### pygame installieren

```bash
pip install pygame
```

### pygame-ce installieren

```bash
pip install pygame-ce
```

---

# ▶ Spiel starten

```bash
python StarWarsGame.py
```

---

# ⚖️ Balancing

Alle wichtigen Gameplay-Werte befinden sich in:

```text
game/constants.py
```

Dort können unter anderem folgende Werte angepasst werden:

- Gegner-Trefferquote
- Gegner-Lebenspunkte
- Gegnergeschwindigkeit
- Gegner-Aggressivität
- Maximale Gegneranzahl
- Gegner-Spawnrate
- Asteroidendichte
- Asteroidengeschwindigkeit
- Asteroidengröße
- Punkteschwellen für Gegner-Freischaltungen
- Schwierigkeitsfaktoren einzelner Sternensysteme

### Beispiel

```python
DIFFICULTY_SETTINGS = {
    "easy": {
        "enemy_accuracy": 0.45,
        "enemy_hp": 0.80,
        "enemy_speed": 0.85,
        "enemy_aggression": 0.70,
    },

    "normal": {
        "enemy_accuracy": 0.65,
        "enemy_hp": 1.00,
        "enemy_speed": 1.00,
        "enemy_aggression": 1.00,
    },

    "hard": {
        "enemy_accuracy": 0.80,
        "enemy_hp": 1.15,
        "enemy_speed": 1.15,
        "enemy_aggression": 1.20,
    },

    "expert": {
        "enemy_accuracy": 0.92,
        "enemy_hp": 1.35,
        "enemy_speed": 1.30,
        "enemy_aggression": 1.40,
    },
}
```

---

# 🧠 KI-Architektur

```text
game/enemies/
├── __init__.py
├── base.py
├── ai.py
├── movement.py
├── weapons.py
├── projectiles.py
├── manager.py
├── config.py
└── audio.py
```

Die Architektur wurde modular aufgebaut und ist für zukünftige Erweiterungen vorbereitet.

Geplante Erweiterungen:

- Bossgegner
- Begleitjäger
- Weitere Fraktionen
- Spezialwaffen
- Koop-Modus
- Wellenmodus
- Neue Gegnerklassen

---

# 📂 Projektstruktur

```text
StarWars/
│
├── StarWarsGame.py
├── README.md
├── requirements.txt
│
└── game/
    ├── assets.py
    ├── background.py
    ├── constants.py
    ├── entities.py
    ├── ui.py
    │
    └── enemies/
        ├── __init__.py
        ├── ai.py
        ├── audio.py
        ├── base.py
        ├── config.py
        ├── manager.py
        ├── movement.py
        ├── projectiles.py
        └── weapons.py
```

---

# 🛣️ Roadmap

## Version 1.1

- Erste Bossgegner
- Neue Gegnerklassen
- Verbesserte Partikeleffekte

## Version 1.2

- Koop-Modus
- Neue Sternensysteme
- Zufällige Weltraum-Events

## Version 2.0

- Story-Kampagne
- Fraktionssystem
- Schiffs-Upgrades
- Anpassbare Raumschiffe

---

# 📸 Screenshots

```text
docs/menu.png
docs/gameplay.png
docs/combat.png
docs/bossfight.png
```

*Sobald erste spielbare Versionen verfügbar sind, können hier Screenshots und GIFs eingefügt werden.*

---

# ⚠️ Rechtlicher Hinweis

Dieses Projekt dient ausschließlich Lern-, Demonstrations- und Entwicklungszwecken.

Star Wars sowie alle zugehörigen Marken, Namen und Designs sind Eigentum von Lucasfilm Ltd. und The Walt Disney Company. Dieses Projekt steht in keiner Verbindung zu den Rechteinhabern.