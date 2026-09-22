# 🚀 Star Wars: Galactic Assault

Ein actionreiches 2D-Arcade-Weltraumspiel mit **Python** und **Pygame**.

Übernimm die Kontrolle über verschiedene Raumschiffe, durchquere dynamische
Sternensysteme, kämpfe gegen KI-Gegner und tritt im lokalen oder LAN-basierten
Mehrspielermodus gegen andere Spieler an.

## ✨ Highlights

- 🚀 4 spielbare Raumschiffe
- 🤖 Dynamisches KI-Gegnersystem
- ☄️ Dynamisches Asteroidensystem
- 🌌 Fortschritt durch mehrere Sternensysteme
- ⚙️ 4 Schwierigkeitsstufen
- 🎮 Lokaler PvP-Modus
- 🌐 LAN-Multiplayer
- 🏆 Score- und Highscore-System
- 💥 Laser, Torpedos und Explosionen

---

## 📑 Inhaltsverzeichnis

- [📦 Installation](#-installation)
- [▶ Spiel starten](#-spiel-starten)

- [🚀 Features](#-features)
  - [🎮 Spielmodi](#-spielmodi)
  - [🚀 Spielbare Schiffe](#-spielbare-schiffe)
  - [☄️ Asteroidensystem](#-asteroidensystem)
  - [💥 Waffen](#-waffen)

- [🌐 Mehrspielermodi](#-mehrspielermodi)
  - [LAN Multiplayer](#lan-multiplayer)
  - [LAN PvP](#lan-pvp)
  - [Lokaler PvP](#lokaler-pvp)

- [🏆 Score-System](#-score-system)

- [⚙️ Schwierigkeitssystem](#️-schwierigkeitssystem)
  - [Verfügbare Schwierigkeitsstufen](#verfügbare-schwierigkeitsstufen)
  - [Balancing & Konfiguration](#balancing--konfiguration)
  - [Gegner-Freischaltungen](#gegner-freischaltungen)
  - [Sternensystem-Skalierung](#sternensystem-skalierung)

- [📈 Progression & Sternensysteme](#-progression--sternensysteme)

- [🧠 KI-System](#-ki-system)
  - [Komponenten](#komponenten)
  - [Gruppenrollen](#gruppenrollen)
  - [Dodge-System](#dodge-system)
  - [Dynamische Schwierigkeit](#dynamische-schwierigkeit)

- [🎯 Spielziel](#-spielziel)
- [🎮 Steuerung](#-steuerung)
- [📂 Projektstruktur](#-projektstruktur)
- [🪐 Planeten & Welten](#-planeten--welten)
- [⚠️ Rechtlicher Hinweis](#️-rechtlicher-hinweis)


---

# 📦 Installation

## Voraussetzungen

- Python **3.8 oder neuer**
- Windows / Linux / macOS
- Eine Netzwerkverbindung wird nur für den LAN-Multiplayer benötigt

## Installation

Repository klonen oder herunterladen:

```bash
git clone https://github.com/Post155/Star-Was-Spiel-Python.git
cd StarWars
```

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

Alternativ kann Pygame direkt installiert werden:

```bash
pip install pygame
```

> 💡 Für eine saubere Entwicklungsumgebung empfiehlt sich zusätzlich eine
> virtuelle Python-Umgebung.

---

# ▶ Spiel starten

Nach der Installation kann das Spiel mit folgendem Befehl gestartet werden:

```bash
python StarWarsGame.py
```

Nach dem Start stehen die verfügbaren Spielmodi über das Mehrspieler-/Spielmenü
zur Auswahl.

> Für LAN-Spielmodi müssen sich die beteiligten Computer im selben lokalen
> Netzwerk befinden.

---

# 🚀 Features

## 🎮 Spielmodi

Das Projekt unterstützt mehrere Spielvarianten:

- 🎮 **Einzelspieler**
- 🌐 **LAN Multiplayer**
- ⚔️ **LAN PvP**
- 🎮 **Lokaler PvP**

Der Einzelspieler konzentriert sich auf Progression, Asteroiden und KI-Gegner.
Die Mehrspielermodi erweitern das Spiel um den Wettbewerb zwischen mehreren
Spielern.

## 🚀 Spielbare Schiffe

- X-Wing
- Millennium Falcon
- TIE-Fighter
- Battle Droid Fighter

Jedes Schiff verfügt über eigene Eigenschaften, Waffen und
Flugcharakteristiken.

## ☄️ Asteroidensystem

Das Asteroidensystem bildet einen zentralen Teil des Gameplays.

- Mehrere Asteroidengrößen
- Individuelle Geschwindigkeiten
- Dynamische Spawnraten
- Steigende Asteroidendichte
- Kollisions- und Schadenssystem
- Fortschrittsabhängige Skalierung

## 💥 Waffen

Die Raumschiffe verfügen über unterschiedliche Waffen:

- Laser
- Torpedos

Laser dienen als reguläre Angriffe, während Torpedos als zusätzliche
Angriffsoption eingesetzt werden.

---

# 🌐 Mehrspielermodi

Das Spiel enthält neben dem Einzelspieler mehrere Mehrspielervarianten.

## LAN Multiplayer

Der LAN-Multiplayer ermöglicht das gemeinsame Spielen über ein lokales
Netzwerk.

### Verbindung

- Die beteiligten PCs befinden sich im selben lokalen Netzwerk.
- Es wird keine externe Server-Infrastruktur benötigt.
- Das Spiel kann über die vorhandenen LAN-Funktionen verbunden werden.

### Spielprinzip

Jeder Spieler spielt mit seiner eigenen Spielansicht und kann gleichzeitig mit
anderen Spielern im selben Match antreten.

Das Score-/Highscore-System dient dabei als gemeinsamer Wettbewerbsrahmen.

## LAN PvP

Im LAN-PvP treten Spieler direkt gegeneinander an.

Die Netzwerkvariante nutzt die vorhandenen PvP-Regeln, Waffen und
Trefferlogiken und erweitert sie um die Netzwerkverbindung zwischen den PCs.

## Lokaler PvP

Der lokale PvP-Modus ermöglicht ein direktes Duell auf **einem einzigen PC**.

Dieser Modus benötigt keine Netzwerkverbindung.

### Lokale Steuerung

**Spieler 1 – unteres Schiff**

- `A / D` → Bewegen
- `W` → Laser
- `S` → Torpedo

**Spieler 2 – oberes Schiff**

- `← / →` → Bewegen
- `↑` → Laser
- `↓` → Torpedo

Die lokale PvP-Steuerung ist ausschließlich für diesen Spielmodus aktiv.
Einzelspieler und Netzwerkmodi verwenden weiterhin ihre vorgesehenen Eingaben.

### Mehrspieler-Menü

1. LAN Multiplayer
2. LAN PvP
3. Lokaler PvP

---

# 🏆 Score-System

Das Spiel verwendet ein Punktesystem für den Spielfortschritt und den
Wettbewerb.

Der Score ist unter anderem relevant für:

- Gegner-Freischaltungen
- Progression
- Highscore
- Mehrspieler-Wettbewerb

Im Einzelspieler ist der Score eng mit der Freischaltung neuer Gegnerstufen
verbunden.

Im Mehrspielermodus können die aktuellen Spielstände der Spieler miteinander
verglichen werden.

---

# ⚙️ Schwierigkeitssystem

Zu Beginn jeder Spielrunde kann eine Schwierigkeitsstufe ausgewählt werden.

## Verfügbare Schwierigkeitsstufen

| Schwierigkeit | Beschreibung |
|---|---|
| Einfach | Ideal für Einsteiger |
| Normal | Ausgewogenes Standard-Erlebnis |
| Schwer | Höhere Herausforderung durch aggressivere Gegner |
| Experte | Maximale Schwierigkeit für erfahrene Spieler |

Die gewählte Schwierigkeit beeinflusst:

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

# ⚖️ Balancing & Konfiguration

Alle wichtigen Gameplay-Werte befinden sich in:

```text
game/constants.py
```

## Difficulty Presets

Über `DIFFICULTY_SETTINGS` können unter anderem folgende Werte angepasst
werden:

- `enemy_accuracy`
- `enemy_hp`
- `enemy_speed`
- `enemy_aggression`
- `enemy_max`
- `enemy_spawn`
- `asteroid_density`
- `asteroid_speed`
- `asteroid_size`

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

## Gegner-Freischaltungen

```python
ENEMY_UNLOCK_STANDARD_POINTS = 1000
ENEMY_UNLOCK_HEAVY_POINTS = 3000
ENEMY_UNLOCK_ELITE_POINTS = 6000
```

Vor **1.000 Punkten** erscheinen keine Gegner.

| Punkte | Freischaltung |
|---:|---|
| 0–999 | Nur Asteroiden |
| 1.000 | Standardgegner |
| 3.000 | Schwere Gegner |
| 6.000 | Elite-Gegner |

## Sternensystem-Skalierung

```python
SYSTEM_DIFFICULTY_BONUS = (
    0.00,  # System 1
    0.15,  # System 2
    0.30,  # System 3
    0.50,  # System 4
)
```

| Sternensystem | Bonus |
|---|---:|
| System 1 | +0 % |
| System 2 | +15 % |
| System 3 | +30 % |
| System 4 | +50 % |

Spätere Systeme verwenden automatisch den zuletzt definierten Wert.

Der Bonus beeinflusst:

- Gegner-Lebenspunkte
- Gegner-Geschwindigkeit
- Gegner-Treffergenauigkeit
- Gegner-Aggressivität
- Asteroidendichte
- Asteroidengeschwindigkeit
- Asteroidengröße

---

# 📈 Progression & Sternensysteme

Zu Beginn befindet sich der Spieler allein im Sternensystem und kämpft
ausschließlich gegen Asteroiden. Dadurch können Steuerung und Waffen zunächst
ohne Druck erlernt werden.

## Gegner-Freischaltung

| Punkte | Ereignis |
|---:|---|
| 0–999 | Nur Asteroiden |
| 1.000 | Erste feindliche Schiffe erscheinen |
| 3.000 | Erweiterte Gegnerklassen werden freigeschaltet |
| 6.000 | Elite-Gegner erscheinen |

Vor jeder neuen Gegnerstufe wird eine Warnmeldung angezeigt.

Beispiele:

```text
⚠ Feindliche Schiffe wurden entdeckt!
⚠ Verstärkte Aktivitäten im System festgestellt!
⚠ Elite-Einheit im Anflug!
⚠ Unbekanntes Signal erkannt!
```

## Dynamische Sternensysteme

Zusätzlich zur gewählten Schwierigkeit erhöht jedes neue Sternensystem die
Gesamtgefahr.

| Sternensystem | Schwierigkeitsbonus |
|---|---:|
| System 1 | +0 % |
| System 2 | +15 % |
| System 3 | +30 % |
| System 4 | +50 % |

Die Skalierung beeinflusst unter anderem:

- Gegnerstärke
- Gegnerverhalten
- Spawnraten
- Asteroidendichte
- Asteroidengeschwindigkeit

Dadurch steigt die Herausforderung mit dem Fortschritt durch die Systeme.

---

# 🧠 KI-System

Die Gegner-KI wurde modular aufgebaut und ist vollständig erweiterbar.

## Komponenten

| Komponente | Aufgabe |
|---|---|
| **EnemyBase** | Lebenspunkte, Hitbox, Sprite und Basisschnittstelle |
| **EnemyBrain** | Zielwahl, Reaktionszeit und Entscheidungslogik |
| **EnemyMovement** | Weiche, beschleunigungsbasierte Bewegung |
| **EnemyWeaponSystem** | Salven, Zielvorhalt und Torpedos |
| **EnemyManager** | Spawnlogik, Schwierigkeit, Gruppenbildung und Score-System |

## Gruppenrollen

### Attacker

Folgt dem Spieler direkt und führt regelmäßige Angriffe aus.

### Flanker Left

Greift versetzt von links an.

### Flanker Right

Greift versetzt von rechts an.

### Support

Bleibt weiter entfernt und unterstützt andere Gegner.

Dadurch bewegen sich mehrere Gegner nicht auf identischen Flugbahnen.

## Dodge-System

Die KI prüft nur in bestimmten Reaktionsintervallen, ob ein Projektil ihre
Flugbahn kreuzt.

Dadurch entstehen keine unrealistisch perfekten Ausweichmanöver und
gleichzeitig bleibt die CPU-Last gering.

- Elite-Gegner reagieren schneller
- Standardgegner reagieren ausgewogen
- Schwere Gegner reagieren träger

## Dynamische Schwierigkeit

Der `EnemyManager` berechnet einen dynamischen Schwierigkeitsfaktor aus:

- aktuellem Sternensystem
- Spielerpunktzahl
- gewähltem Schwierigkeitsgrad

Beeinflusst werden:

- Maximale Gegnerzahl
- Spawnintervall
- Geschwindigkeit
- Feuerfrequenz
- Zielgenauigkeit
- Elite-Wahrscheinlichkeit
- Torpedonutzung

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

## Einzelspieler

| Taste | Aktion |
|---|---|
| `A / ←` | Nach links bewegen |
| `D / →` | Nach rechts bewegen |
| `W / ↑` | Nach oben bewegen |
| `Leertaste` | Laser schießen |
| `S / ↓` | Torpedo abfeuern |
| `H` | Hitboxen anzeigen |
| `1 / 2 / 3 / 4` | Schiff wechseln (Debug) |
| `ESC` | Pause / Zurück |

## Lokaler PvP

### Spieler 1 – unteres Schiff

| Taste | Aktion |
|---|---|
| `A / D` | Bewegen |
| `W` | Laser |
| `S` | Torpedo |

### Spieler 2 – oberes Schiff

| Taste | Aktion |
|---|---|
| `← / →` | Bewegen |
| `↑` | Laser |
| `↓` | Torpedo |

> Die lokale PvP-Steuerung ist ausschließlich im lokalen PvP-Modus aktiv.

---

# 📂 Projektstruktur

```text
StarWars/
│
├── StarWarsGame.py       # Hauptprogramm
├── README.md             # Projektdokumentation
├── requirements.txt      # Python-Abhängigkeiten
│
└── game/
    ├── assets.py         # Assets und Grafiken
    ├── background.py     # Hintergrundsystem
    ├── constants.py      # Globale Konfiguration
    ├── entities.py       # Spielobjekte
    ├── ui.py             # Benutzeroberfläche
    │
    └── enemies/
        ├── __init__.py
        ├── ai.py
        ├── base.py
        ├── config.py
        ├── manager.py
        ├── movement.py
        ├── projectiles.py
        ├── weapons.py
        └── audio.py
```
---

# 🪐 Planeten & Welten

Die verfügbaren Welten und Weltraumobjekte befinden sich unter
`Pixelarts/Planets`.

| Welt | Asset |
|---|---|
| Tatooine | ![Tatooine](Pixelarts/Planets/core_worlds/planet_tatooine.png) |
| Kamino |  ![Kamino](Pixelarts/Planets/core_worlds/planet_kamino.png) |
| Coruscant |  ![Coruscant](Pixelarts/Planets/core_worlds/planet_corusant.png) |
| Hoth |  ![Hoth](Pixelarts/Planets/core_worlds/planet_hoth.png) |
| Endor |  ![Endor](Pixelarts/Planets/core_worlds/planet_endor.png) |
| Mustafar | ![Mustafar](Pixelarts/Planets/core_worlds/planet_Mustafar.png) |
| Earth | ![Earth](Pixelarts/Planets/milkyway/planet_earth.png) |
| Saturn | ![Saturn](Pixelarts/Planets/milkyway/planet_saturn.png) |
| Schwarzes Loch | ![Schwarzes Loch](Pixelarts/Planets/milkyway/planet_schwarzesLoch.png) |
| Purpurplanet | ![Purpurplanet](Pixelarts/Planets/core_worlds/planet_purple.png) |
| Todesstern | ![Todesstern](Pixelarts/Planets/death_star/TodesternEins.png) |
| Todesstern II | ![Todesstern](Pixelarts/Planets/death_star/TodesternZwei.png) |
| Sternzerstörer | ![Sternzerstörer](Pixelarts/Planets/death_star/Sternzerstörer.png) |


### Die Welt-Assets dienen als visuelle Bestandteile der verschiedenen Sternensysteme.

---

# ⚠️ Rechtlicher Hinweis

Dieses Projekt wurde ausschließlich zu **Lern-, Demonstrations- und
Entwicklungszwecken** erstellt.

**Star Wars** sowie die damit verbundenen Namen, Charaktere, Designs und
Marken gehören ihren jeweiligen Rechteinhabern.

Dieses Fanprojekt steht in keiner offiziellen Verbindung zu den Rechteinhabern.
