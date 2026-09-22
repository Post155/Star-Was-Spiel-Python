# 🚀 Star Wars: Galactic Assault

Ein actionreiches 2D-Arcade-Weltraumspiel, entwickelt mit **Python** und **Pygame**.

Übernimm die Kontrolle über verschiedene Raumschiffe, durchquere dynamische Sternensysteme, kämpfe gegen KI-Gegner und tritt in verschiedenen lokalen und LAN-basierten Mehrspielermodi an.

Das Projekt wurde als **Lern-, Entwicklungs- und Demonstrationsprojekt** erstellt.

---

## ✨ Highlights

* 🚀 4 spielbare Raumschiffe
* 🤖 Dynamisches KI-Gegnersystem
* ☄️ Dynamisches Asteroidensystem
* 🌌 Mehrere Sternensysteme und Welten
* ⚙️ 4 Schwierigkeitsstufen
* 🎮 Einzelspieler
* 🏆 Punktekampf
* ⚔️ Letzter Überlebender
* 🌐 LAN-Multiplayer
* 🖥️ Lokaler Mehrspielermodus
* 📊 Echtzeit-Score- und Ranglistensystem
* 💥 Laser und Torpedos
* ❤️ 3-Leben-System
* 🌠 Pixel-Art-Grafiken und dynamische Weltraumhintergründe

---

# 📑 Inhaltsverzeichnis

* [📦 Installation](#-installation)

  * [Voraussetzungen](#voraussetzungen)
  * [Automatische Installation unter Windows](#automatische-installation-unter-windows)
  * [Manuelle Installation](#manuelle-installation)
* [▶️ Spiel starten](#️-spiel-starten)
* [🚀 Features](#-features)

  * [🎮 Spielmodi](#-spielmodi)
  * [🚀 Spielbare Schiffe](#-spielbare-schiffe)
  * [☄️ Asteroidensystem](#️-asteroidensystem)
  * [💥 Waffen](#-waffen)
* [🌐 Mehrspielermodi](#-mehrspielermodi)

  * [🏆 Punktekampf](#-punktekampf)
  * [⚔️ Letzter Überlebender](#️-letzter-überlebender)
  * [🌐 LAN](#-lan)
  * [🖥️ Lokaler Mehrspielermodus](#️-lokaler-mehrspielermodus)
* [🏆 Score-System](#-score-system)
* [⚙️ Schwierigkeitssystem](#️-schwierigkeitssystem)
* [📈 Progression & Sternensysteme](#-progression--sternensysteme)
* [🧠 KI-System](#-ki-system)
* [🎯 Spielziel](#-spielziel)
* [🎮 Steuerung](#-steuerung)
* [📂 Projektstruktur](#-projektstruktur)
* [🪐 Planeten & Welten](#-planeten--welten)
* [🔧 Fehlerbehebung](#-fehlerbehebung)
* [⚠️ Rechtlicher Hinweis](#️-rechtlicher-hinweis)

---

# 📦 Installation

## Voraussetzungen

Für die Ausführung des Spiels werden benötigt:

* **Python 3.8 oder neuer**
* **Pygame 2.5 oder neuer**
* Windows, Linux oder macOS
* Für LAN-Modi: ein gemeinsames lokales Netzwerk

> **Hinweis:** Die bereitgestellten `.bat`-Dateien sind für **Windows** vorgesehen.

---

## Automatische Installation unter Windows

Für Windows wird die Verwendung der mitgelieferten Installationsdatei empfohlen.

Im Projektordner befinden sich:

```text
install.bat
start.bat
requirements.txt
```

### 1. Installation

Einmalig:

```text
install.bat
```

ausführen.

Das Installationsskript:

1. sucht nach einer vorhandenen Python-Installation,
2. erstellt im Projektordner eine virtuelle Python-Umgebung,
3. installiert `pip` innerhalb dieser Umgebung,
4. installiert die benötigten Python-Abhängigkeiten,
5. installiert Pygame innerhalb der virtuellen Umgebung.

Die virtuelle Umgebung befindet sich anschließend unter:

```text
.venv/
```

### Warum eine virtuelle Umgebung?

Das Projekt verwendet eine eigene virtuelle Python-Umgebung.

Dadurch werden die für das Spiel benötigten Python-Pakete nicht in die globale Python-Installation des Computers installiert.

Die Struktur sieht anschließend beispielsweise so aus:

```text
Star-Wars-Spiel/
│
├── .venv/
├── install.bat
├── start.bat
├── requirements.txt
├── StarWarsGame.py
├── game/
└── Pixelarts/
```

> Die `.venv` sollte normalerweise **nicht in Git eingecheckt oder mit dem Projekt verteilt werden**. Sie kann auf jedem Computer mit `install.bat` neu erstellt werden.

---

## Manuelle Installation

Falls die automatische Installation nicht verwendet werden soll, kann die Umgebung auch manuell eingerichtet werden.

### Virtuelle Umgebung erstellen

Windows:

```powershell
py -m venv .venv
```

Linux/macOS:

```bash
python3 -m venv .venv
```

### Virtuelle Umgebung aktivieren

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### Abhängigkeiten installieren

```bash
python -m pip install -r requirements.txt
```

Die aktuelle `requirements.txt` enthält:

```text
pygame>=2.5
```

---

# ▶️ Spiel starten

## Windows

Nach der Installation kann das Spiel über:

```text
start.bat
```

gestartet werden.

`start.bat` verwendet ausschließlich:

```text
.venv\Scripts\python.exe
```

und startet dadurch das Spiel innerhalb der virtuellen Umgebung.

Alternativ kann das Spiel innerhalb der aktivierten virtuellen Umgebung manuell gestartet werden:

```bash
python StarWarsGame.py
```

---

## ⚠️ Wichtiger Hinweis zur Installation

Das Installationsskript setzt voraus, dass Python auf dem System bereits vorhanden ist.

Falls Python nicht gefunden wird, muss Python zunächst über eine vertrauenswürdige Quelle installiert werden.

Für Windows wird die offizielle Python-Distribution empfohlen:

```text
https://www.python.org/
```

Die Installationsdateien von Python und Pygame stammen nicht aus diesem Projekt.

---

# 🚀 Features

## 🎮 Spielmodi

Das Spiel besitzt mehrere voneinander getrennte Spielmodi:

* 🎮 **Einzelspieler**
* 🏆 **Punktekampf**
* ⚔️ **Letzter Überlebender**
* 🌐 **LAN-Spielmodi**
* 🖥️ **Lokaler Mehrspielermodus**

Die beiden PvP-orientierten Hauptmodi **Punktekampf** und **Letzter Überlebender** verwenden unterschiedliche Spielregeln.

---

# 🏆 Punktekampf

Der Punktekampf ist **kein klassischer PvP-Kampf**.

Er basiert auf dem Einzelspieler-Gameplay.

Das Grundprinzip:

> Jeder Spieler spielt gleichzeitig seine **eigene Einzelspieler-Runde** und vergleicht seinen Score mit den anderen Spielern.

### Jeder Spieler besitzt seine eigene Spielwelt

Jeder Spieler hat:

* eigenes Schiff
* eigene Asteroiden
* eigene KI-Gegner
* eigene Projektile
* eigene Kollisionen
* eigenen Score
* eigenes Sternensystem
* eigenes Leben-System
* eigene Spielprogression

Die Spielwelt eines Spielers wird nicht durch die Spielwelt eines anderen Spielers beeinflusst.

### Ghost-Spieler

Andere Spieler werden ausschließlich als **Geister/Ghost-Spieler** dargestellt.

Ein Ghost dient nur zur Anzeige von:

* Spielername
* Position
* Schiffstyp
* Punktestand
* aktuellem Sternensystem

Ghost-Spieler:

* besitzen keine Kollisions-Hitbox,
* können nicht getroffen werden,
* können keinen Schaden verursachen,
* können keinen Schaden erhalten,
* können nicht beschossen werden,
* können nicht mit Asteroiden kollidieren,
* können keine KI-Gegner beeinflussen,
* können keine Projektile beeinflussen,
* beeinflussen die eigene Spielwelt nicht.

Der Ghost ist damit ausschließlich eine **visuelle Netzwerkdarstellung**.

### Netzwerkdaten im Punktekampf

Für die Ghost-Darstellung werden nur die dafür benötigten Informationen übertragen:

```text
Spielername
Schiffstyp
X-Position
Y-Position
Punktestand
Sternensystem
```

Es werden für den Punktekampf keine PvP-Treffer oder PvP-Schadensereignisse benötigt.

### Spielziel

Nach dem Ende der Runde werden die Punktestände miteinander verglichen.

Der Spieler mit dem höchsten Score erzielt die höchste Platzierung.

---

# ⚔️ Letzter Überlebender

Der Modus **Letzter Überlebender** ist ein echter PvP-Modus.

Hier kämpfen die Spieler direkt gegeneinander.

### Spielprinzip

* Spieler können sich gegenseitig beschießen.
* Laser können gegnerische Spieler treffen.
* Torpedos können gegnerische Spieler treffen.
* Treffer verursachen Schaden.
* Spieler können Leben verlieren.
* Ein Spieler kann einen anderen Spieler besiegen.
* Der letzte noch lebende Spieler gewinnt die Runde.

### Spielfeld

Die Spieler stehen sich gegenüber:

```text
        Spieler 2
           ↓

     gemeinsames
      Spielfeld

           ↑
        Spieler 1
```

Spieler 1 startet im unteren Bereich.

Spieler 2 startet im oberen Bereich.

Im Gegensatz zum Punktekampf verwenden beide Spieler hier **eine gemeinsame PvP-Spielwelt**.

### Asteroiden

Asteroiden bleiben aktiv.

Es werden jedoch keine KI-Gegner eingesetzt.

Asteroiden können unter anderem auf folgenden symmetrischen Bahnen auftreten:

```text
links  → rechts
rechts → links

links unten → rechts oben
rechts unten → links oben

links oben → rechts unten
rechts oben → links unten
```

Die Flugbahnen werden so angelegt, dass nicht dauerhaft eine Spielfeldhälfte bevorzugt wird.

---

# 🔀 Technische Trennung der Mehrspielermodi

Die beiden Modi verfolgen unterschiedliche technische Konzepte.

```text
PUNKTEKAMPF
│
├── eigene Einzelspieler-Welt
├── eigene KI
├── eigene Asteroiden
├── eigene Projektile
├── eigener Score
├── eigenes Sternensystem
└── Ghost-Spieler als reine Anzeige


LETZTER ÜBERLEBENDER
│
├── gemeinsame PvP-Welt
├── Spieler gegen Spieler
├── PvP-Projektile
├── PvP-Schaden
├── Treffer
├── Leben
└── Abschüsse
```

Die Spielmodi sollen dadurch unterschiedliche Spielerlebnisse bieten und nicht dieselben Kampfregeln verwenden.

---

# 🌐 LAN

Die LAN-Funktionen ermöglichen Mehrspielerpartien innerhalb eines lokalen Netzwerks.

### Voraussetzungen

* Die beteiligten Computer müssen sich im selben lokalen Netzwerk befinden.
* Eine Internetverbindung ist für die eigentliche LAN-Verbindung nicht erforderlich.
* Die Kommunikation erfolgt zwischen den beteiligten Computern.
* Ein externer Spielserver wird für die LAN-Verbindung nicht benötigt.

Ein Netzwerk-Switch oder ein entsprechendes lokales Netzwerk kann verwendet werden.

### Netzwerkbedingungen

Die tatsächliche Verbindungsqualität kann unter anderem von folgenden Faktoren abhängen:

* Netzwerkhardware
* Firewall-Einstellungen
* Betriebssystem
* IP-Konfiguration
* Auslastung des lokalen Netzwerks
* Sicherheitssoftware

Das Projekt übernimmt keine Garantie dafür, dass eine Verbindung in jeder Netzwerkumgebung hergestellt werden kann.

---

# 🖥️ Lokaler Mehrspielermodus

Der lokale Mehrspielermodus ermöglicht das Spielen mehrerer Spieler auf einem einzelnen Computer, soweit der jeweilige Spielmodus dies unterstützt.

Der lokale PvP-Modus verwendet unterschiedliche Eingaben für die beiden Spieler.

## Spieler 1 – unteres Schiff

| Taste   | Aktion  |
| ------- | ------- |
| `A / D` | Bewegen |
| `W`     | Laser   |
| `S`     | Torpedo |

## Spieler 2 – oberes Schiff

| Taste   | Aktion  |
| ------- | ------- |
| `← / →` | Bewegen |
| `↑`     | Laser   |
| `↓`     | Torpedo |

Diese Steuerung ist für den lokalen PvP-Modus vorgesehen.

---

# 🏆 Score-System

Das Spiel verwendet ein Punktesystem für den Spielfortschritt und den Wettbewerb.

Punkte können unter anderem durch das Zerstören von:

* Asteroiden
* KI-Gegnern

erreicht werden.

Im Punktekampf dient der Score als zentrale Vergleichsgröße zwischen den Spielern.

Eine Rangliste kann während des Mehrspielerspiels den aktuellen Stand anzeigen.

Angezeigt werden können unter anderem:

* Platzierung
* Spielername
* Punktestand
* aktuelles Sternensystem

---

# ⚙️ Schwierigkeitssystem

Zu Beginn einer Spielrunde kann eine Schwierigkeitsstufe ausgewählt werden.

## Verfügbare Schwierigkeitsstufen

| Schwierigkeit | Beschreibung              |
| ------------- | ------------------------- |
| Einfach       | Geringere Herausforderung |
| Normal        | Standard-Spielbalance     |
| Schwer        | Erhöhte Herausforderung   |
| Experte       | Sehr hohe Herausforderung |

Die konkrete Balance kann sich mit der jeweiligen Version des Spiels ändern.

Je nach Konfiguration können unter anderem beeinflusst werden:

* Gegnerische Trefferquote
* Gegner-Lebenspunkte
* Gegnergeschwindigkeit
* Gegner-Aggressivität
* Verfolgungsverhalten
* Gegner-Spawnrate
* Maximale Anzahl aktiver Gegner
* Asteroidendichte
* Asteroidengeschwindigkeit
* Asteroidengröße

---

# ⚖️ Balancing & Konfiguration

Wichtige Gameplay-Konfigurationen befinden sich unter anderem in:

```text
game/constants.py
```

Je nach Version können dort beispielsweise Werte für Schwierigkeitsstufen, Spawnraten und Skalierungsfaktoren definiert sein.

Beispielsweise können Konfigurationen dieser Art verwendet werden:

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

> Diese Werte dienen der Dokumentation des Konzepts. Die tatsächlich verwendeten Werte können sich zwischen verschiedenen Versionen des Projekts ändern.

---

# 🔓 Gegner-Freischaltungen

In der aktuellen Spielkonzeption werden Gegner abhängig vom erreichten Score freigeschaltet.

Beispielhafte Schwellenwerte:

```python
ENEMY_UNLOCK_STANDARD_POINTS = 1000
ENEMY_UNLOCK_HEAVY_POINTS = 3000
ENEMY_UNLOCK_ELITE_POINTS = 6000
```

| Punkte | Freischaltung  |
| -----: | -------------- |
|  0–999 | Nur Asteroiden |
|  1.000 | Standardgegner |
|  3.000 | Schwere Gegner |
|  6.000 | Elite-Gegner   |

Die tatsächlichen Werte sind konfigurationsabhängig und können sich in zukünftigen Versionen ändern.

---

# 🌌 Sternensystem-Skalierung

Mit fortschreitendem Spiel können zusätzliche Schwierigkeitsfaktoren angewendet werden.

Beispiel:

```python
SYSTEM_DIFFICULTY_BONUS = (
    0.00,  # System 1
    0.15,  # System 2
    0.30,  # System 3
    0.50,  # System 4
)
```

| Sternensystem | Beispielhafter Bonus |
| ------------- | -------------------: |
| System 1      |                 +0 % |
| System 2      |                +15 % |
| System 3      |                +30 % |
| System 4      |                +50 % |

Je nach Implementierung können unter anderem folgende Faktoren skaliert werden:

* Gegner-Lebenspunkte
* Gegnergeschwindigkeit
* Gegner-Treffergenauigkeit
* Gegner-Aggressivität
* Asteroidendichte
* Asteroidengeschwindigkeit
* Asteroidengröße

---

# 📈 Progression & Sternensysteme

Zu Beginn einer Spielrunde liegt der Schwerpunkt zunächst auf dem Asteroidensystem.

Mit zunehmendem Score können weitere Gegnerklassen freigeschaltet werden.

Beispiel:

| Punkte | Ereignis                 |
| -----: | ------------------------ |
|  0–999 | Nur Asteroiden           |
|  1.000 | Erste feindliche Schiffe |
|  3.000 | Erweiterte Gegnerklassen |
|  6.000 | Elite-Gegner             |

Zusätzlich kann sich die Schwierigkeit durch den Wechsel in weitere Sternensysteme erhöhen.

---

# 🧠 KI-System

Die Gegner-KI ist modular aufgebaut.

## Komponenten

| Komponente            | Aufgabe                         |
| --------------------- | ------------------------------- |
| **EnemyBase**         | Basiseigenschaften von Gegnern  |
| **EnemyBrain**        | Zielwahl und Entscheidungslogik |
| **EnemyMovement**     | Gegnerbewegung                  |
| **EnemyWeaponSystem** | Gegnerische Waffen und Angriffe |
| **EnemyManager**      | Spawn- und Gegnerverwaltung     |

## Gruppenrollen

### Attacker

Greift den Spieler direkt an.

### Flanker Left

Greift aus einer seitlich versetzten Position an.

### Flanker Right

Greift aus der entgegengesetzten Seite an.

### Support

Unterstützt andere Gegner aus einer größeren Entfernung.

---

# 🎯 Spielziel

## Einzelspieler

Das Ziel besteht darin, möglichst lange zu überleben und einen hohen Score zu erreichen.

Dazu müssen unter anderem:

* Asteroiden zerstört,
* KI-Gegner bekämpft,
* Projektilen ausgewichen,
* Sternensysteme durchquert und
* Leben möglichst lange erhalten

werden.

## Punktekampf

Im Punktekampf steht der Vergleich der erreichten Punktzahlen im Mittelpunkt.

Jeder Spieler spielt dabei seine eigene Einzelspieler-Spielwelt.

## Letzter Überlebender

Im Modus „Letzter Überlebender“ besteht das Ziel darin, den direkten PvP-Kampf zu überstehen.

Der letzte noch lebende Spieler gewinnt die Runde.

---

# 🎮 Steuerung

## Einzelspieler

| Taste           | Aktion                  |
| --------------- | ----------------------- |
| `A / ←`         | Nach links bewegen      |
| `D / →`         | Nach rechts bewegen     |
| `W / ↑`         | Nach oben bewegen       |
| `Leertaste`     | Laser schießen          |
| `S / ↓`         | Torpedo abfeuern        |
| `H`             | Hitboxen anzeigen       |
| `1 / 2 / 3 / 4` | Schiff wechseln – Debug |
| `ESC`           | Pause / Zurück          |

> Einzelne Debug-Tasten können in veröffentlichten Versionen deaktiviert oder geändert werden.

## Lokaler PvP

### Spieler 1 – unteres Schiff

| Taste   | Aktion  |
| ------- | ------- |
| `A / D` | Bewegen |
| `W`     | Laser   |
| `S`     | Torpedo |

### Spieler 2 – oberes Schiff

| Taste   | Aktion  |
| ------- | ------- |
| `← / →` | Bewegen |
| `↑`     | Laser   |
| `↓`     | Torpedo |

---

# ❤️ Leben-System

Im Einzelspieler und im Modus **Letzter Überlebender** wird ein Leben-System verwendet.

Ein Spieler startet mit:

```text
3 Leben
```

Die Leben werden durch Lichtschwertsymbole dargestellt.

Für jedes verlorene Leben verschwindet ein Symbol.

Wenn keine Leben mehr vorhanden sind, gilt der Spieler als besiegt.

> Im Punktekampf besitzt jeder Spieler seine eigene Spielwelt und damit auch sein eigenes Spielgeschehen. Andere Spieler können dieses Leben-System nicht beeinflussen.

---

# 📂 Projektstruktur

Die Projektstruktur kann je nach Entwicklungsstand leicht variieren.

Eine typische Struktur des Projekts ist:

```text
Star-Wars-Spiel-Python/
│
├── StarWarsGame.py
├── README.md
├── requirements.txt
├── install.bat
├── start.bat
│
├── game/
│   ├── __init__.py
│   ├── assets.py
│   ├── constants.py
│   ├── entities.py
│   ├── entities_old.py
│   ├── highscore.py
│   ├── local_pvp.py
│   ├── multiplayer.py
│   ├── network.py
│   ├── pvp_duel.py
│   ├── pvp_input.py
│   ├── scoreboard.py
│   │
│   ├── background/
│   │   ├── manager.py
│   │   ├── objects.py
│   │   ├── planet_manager.py
│   │   ├── starfield.py
│   │   ├── systems.py
│   │   ├── system_manager.py
│   │   └── transition_manager.py
│   │
│   ├── entities/
│   │   ├── asteroid.py
│   │   ├── explosion.py
│   │   ├── player.py
│   │   ├── projectiles.py
│   │   └── ships.py
│   │
│   ├── enemies/
│   │   ├── ai.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── manager.py
│   │   ├── movement.py
│   │   ├── projectiles.py
│   │   └── weapons.py
│   │
│   └── ui/
│       ├── common.py
│       ├── death.py
│       ├── difficulty.py
│       ├── faction.py
│       ├── multiplayer.py
│       └── ship.py
│
└── Pixelarts/
    ├── Astroids/
    ├── Planets/
    ├── Battle_Droid.png
    ├── Explosion.png
    ├── Galactic-Empire-Logo.png
    ├── Hyperraum.png
    ├── lichtschwerter.png
    ├── millennium.png
    ├── Star-Wars-Rebel-Logo.png
    ├── tie-fighter.png
    ├── Torpedo.png
    └── X_Wing.png
```

---

# 🪐 Planeten & Welten

Die Welt- und Weltraumgrafiken befinden sich unter:

```text
Pixelarts/Planets/
```

Unter anderem sind folgende Welten bzw. Objekte vorhanden:

| Welt / Objekt  | Asset                               |
| -------------- | ----------------------------------- |
| Tatooine       | `core_worlds/planet_tatooine.png`   |
| Kamino         | `core_worlds/planet_kamino.png`     |
| Coruscant      | `core_worlds/planet_corusant.png`   |
| Hoth           | `core_worlds/planet_hoth.png`       |
| Endor          | `core_worlds/planet_endor.png`      |
| Mustafar       | `core_worlds/planet_Mustafar.png`   |
| Earth          | `milkyway/planet_earth.png`         |
| Saturn         | `milkyway/planet_saturn.png`        |
| Schwarzes Loch | `milkyway/planet_schwarzesLoch.png` |
| Purpurplanet   | `core_worlds/planet_purple.png`     |
| Todesstern     | `death_star/TodesternEins.png`      |
| Todesstern II  | `death_star/TodesternZwei.png`      |
| Sternzerstörer | `death_star/Sternzerstörer.png`     |

Die Assets dienen der visuellen Darstellung der verschiedenen Spielwelten und Sternensysteme.

---

# 🔧 Fehlerbehebung

## Python wird nicht gefunden

Wenn `install.bat` meldet, dass Python nicht gefunden wurde:

1. Python installieren.
2. Eine unterstützte Python-Version verwenden.
3. Danach `install.bat` erneut ausführen.

## `.venv` wurde nicht gefunden

Wenn `start.bat` meldet:

```text
Die virtuelle Python-Umgebung wurde nicht gefunden.
```

zuerst:

```text
install.bat
```

ausführen.

## Pygame fehlt

Wenn Pygame nicht gefunden wird, `install.bat` erneut ausführen.

Alternativ kann innerhalb der virtuellen Umgebung installiert werden:

```bash
python -m pip install -r requirements.txt
```

## LAN funktioniert nicht

Mögliche Ursachen:

* Computer befinden sich nicht im selben Netzwerk.
* Windows-Firewall blockiert die Verbindung.
* Eine Sicherheitssoftware blockiert die Anwendung.
* IP-Adresse oder Port sind nicht erreichbar.
* Das Netzwerk erlaubt keine direkte Kommunikation zwischen den Geräten.

Das Projekt kann die Konfiguration eines fremden Netzwerks oder einer Firewall nicht garantieren.

## Spiel startet nicht

Zunächst prüfen:

```text
Python-Version
Pygame-Installation
Projektdateien
Asset-Dateien
Firewall
```

Fehlermeldungen aus der Konsole können bei der Fehlersuche hilfreich sein.

---

# 🧪 Entwicklungsstatus

Das Projekt befindet sich in Entwicklung.

Daher können sich zwischen verschiedenen Versionen unter anderem ändern:

* Gameplay
* Balancing
* Steuerung
* Spielmodi
* Netzwerkfunktionen
* Dateistruktur
* Assets
* Python-/Pygame-Anforderungen
* Fehlerbehandlung
* Benutzeroberfläche

Eine bestimmte Funktion oder Spielmechanik wird nur dann als dauerhaft garantiert betrachtet, wenn sie in der jeweiligen veröffentlichten Version ausdrücklich entsprechend dokumentiert ist.

---

# ⚠️ Rechtlicher Hinweis

## Fanprojekt und Markenrechte

**Star Wars** sowie damit verbundene Namen, Figuren, Logos, Designs, Fahrzeuge, Orte und andere geschützte Inhalte sind Eigentum der jeweiligen Rechteinhaber.

Dieses Projekt ist ein **nicht offizielles Fan-, Lern- und Entwicklungsprojekt**.

Es besteht keine behauptete oder beabsichtigte offizielle Verbindung, Partnerschaft, Unterstützung oder Autorisierung durch die jeweiligen Rechteinhaber.

Die Verwendung entsprechender Namen oder Bezeichnungen in dieser Dokumentation dient der Beschreibung des Projekts.

## Keine kommerzielle Zugehörigkeit

Dieses Projekt soll nicht den Eindruck erwecken, dass es von den Rechteinhabern veröffentlicht, unterstützt oder autorisiert wurde.

Falls einzelne Inhalte des Projekts Rechte Dritter berühren, bleiben die entsprechenden Rechte bei den jeweiligen Rechteinhabern.

Für eine öffentliche oder kommerzielle Veröffentlichung sollte vorab geprüft werden, ob für verwendete Namen, Marken, Grafiken, Sounds, Modelle oder sonstige Inhalte entsprechende Rechte oder Lizenzen erforderlich sind.

---

# ⚖️ Haftungs- und Nutzungshinweis

Die Software wird, soweit gesetzlich zulässig, **ohne Zusicherung einer bestimmten Beschaffenheit oder Eignung für einen bestimmten Zweck** bereitgestellt.

Die Nutzung erfolgt grundsätzlich auf eigene Verantwortung.

Es kann trotz sorgfältiger Entwicklung nicht garantiert werden, dass:

* die Software auf jedem Computersystem funktioniert,
* alle Python- und Pygame-Versionen kompatibel sind,
* das Spiel jederzeit fehlerfrei läuft,
* alle Netzwerkumgebungen unterstützt werden,
* alle Hardware- und Treiberkonfigurationen kompatibel sind,
* keine Daten verloren gehen,
* keine Abstürze oder sonstigen technischen Probleme auftreten.

Der Entwickler übernimmt, soweit gesetzlich zulässig, keine Verantwortung für Schäden oder Beeinträchtigungen, die ausschließlich durch die Nutzung der Software entstehen.

Dies gilt insbesondere für Probleme, die durch:

* fehlerhafte Systemkonfiguration,
* inkompatible Hardware,
* inkompatible Software,
* Drittanbieter-Software,
* Netzwerkprobleme,
* Firewall- oder Sicherheitseinstellungen,
* Änderungen am Quellcode durch Dritte,
* nicht vorgesehene Änderungen an Projektdateien

verursacht werden.

**Zwingende gesetzliche Haftungsansprüche bleiben von diesem Hinweis unberührt.** Insbesondere soll dieser Hinweis keine Haftung ausschließen, soweit ein Haftungsausschluss nach dem jeweils anwendbaren Recht nicht zulässig ist.

---

# 🔒 Drittanbieter-Software

Das Projekt verwendet externe Software bzw. Bibliotheken, insbesondere:

* **Python**
* **Pygame**

Für diese Software gelten die jeweiligen Lizenzbedingungen und rechtlichen Hinweise der jeweiligen Rechteinhaber bzw. Anbieter.

Dieses Projekt übernimmt keine Verantwortung für Änderungen, Sicherheitsprobleme oder Fehler in Drittanbieter-Software.

Bei einer Weitergabe des Projekts sollten die jeweils geltenden Lizenzbedingungen der verwendeten Drittanbieter-Komponenten beachtet werden.

---

# 📜 Lizenz und Inhalte

Sofern für einzelne Dateien oder Inhalte dieses Projekts keine eigene Lizenz angegeben ist, sollte nicht automatisch davon ausgegangen werden, dass diese frei kopiert, verändert oder kommerziell verwendet werden dürfen.

Für Inhalte Dritter gelten deren jeweilige Rechte und Lizenzbedingungen.

Bei Unsicherheit über die Verwendung eines Assets sollte vor der Weitergabe oder Veröffentlichung geprüft werden, ob eine entsprechende Nutzung erlaubt ist.

---

# 📌 Hinweis für Nutzer

Durch die Installation oder Verwendung dieser Software wird keine Garantie dafür übernommen, dass die Software auf jedem System ohne Anpassungen funktioniert.

Bei Problemen sollte zunächst geprüft werden, ob:

1. eine unterstützte Python-Version verwendet wird,
2. die virtuelle Umgebung korrekt erstellt wurde,
3. die benötigten Abhängigkeiten installiert wurden,
4. alle Projektdateien vorhanden sind,
5. die verwendeten Assets an den erwarteten Speicherorten liegen,
6. das Betriebssystem und die Firewall die erforderlichen Funktionen zulassen.

---

## 🚀 Viel Spaß beim Spielen!

**Star Wars: Galactic Assault** ist ein eigenständiges Lern- und Entwicklungsprojekt mit Fokus auf Python, Pygame, Spielentwicklung, KI, Netzwerkprogrammierung und Multiplayer-Systeme.
