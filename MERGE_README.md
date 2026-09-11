# Star Wars – Kombinierte Spielversion

Diese Version kombiniert die beiden Spielstände:

- **Asteroiden-System** aus der ursprünglichen Spielversion
- **KI-Gegnersystem** aus `StarWars_KI_Gegnersystem`
- Beide Systeme laufen gleichzeitig im selben Game Loop.
- Spieler-Schüsse können weiterhin Asteroiden und KI-Gegner treffen.
- KI-Gegner können den Spieler mit Lasern/Torpedos angreifen.
- Kollisionen mit Asteroiden verursachen weiterhin Schaden und Explosionen.
- Fenster-Resize, Schiffsauswahl, Fraktionen, Punkte, Leben und Hintergrund-Systemwechsel bleiben erhalten.

## Start

Im Projektordner:

```bash
pip install -r requirements.txt
python StarWarsGame.py
```

## Steuerung

- **A / Pfeil links:** nach links
- **D / Pfeil rechts:** nach rechts
- **Space / W / Pfeil hoch:** Laser
- **S / Pfeil runter:** Torpedo
- **H:** Hitboxen anzeigen
- **1–4:** Schiff wechseln
- **ESC:** aktuelle Runde verlassen

Die Asteroiden und Gegner werden unabhängig voneinander verwaltet und können deshalb gleichzeitig auf dem Bildschirm erscheinen.
