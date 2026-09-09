# KI-Gegnersystem – technische Übersicht

## Gegenschiff-Regel

Die Zuordnung liegt zentral in `game/enemies/config.py` und wird bei jedem Spawn neu aus dem aktuellen Spielerschiff bestimmt. Beim Debug-Schiffswechsel (`1–4`) werden bestehende Gegner gelöscht, damit niemals ein inzwischen gleiches Schiff aktiv bleiben kann.

| Spieler | KI-Gegner |
| --- | --- |
| XWing | TieFighter |
| MillenniumFalcon | BattleDroid |
| Tiefighter | XWing |
| BattleDroid | MillenniumFalcon |

## Komponenten

- `EnemyBase`: Lebenspunkte, Hitbox, Sprite, Trefferblitz, Basisschnittstelle
- `EnemyBrain`: Zielwahl, Reaktionsverzögerung, Dodge-Entscheidung, Rollenverhalten
- `EnemyMovement`: weiches beschleunigungsbegrenztes Steering
- `EnemyWeaponSystem`: Salven, Zielvorhalt, Genauigkeit, taktische Torpedos
- `EnemyManager`: Spawn, Schwierigkeit, Gruppenzusammenstellung, Kollisionen, Score und Explosionen
- `EnemyAudio`: optionaler Explosion-Sound mit sicherem Fallback

## Gruppenrollen

- `attacker`: folgt dem Spieler direkter und führt gelegentliche Dives aus
- `flanker_left`: versetzt seinen Zielpunkt links vom Spieler
- `flanker_right`: versetzt seinen Zielpunkt rechts vom Spieler
- `support`: bleibt höher und unterstützt aus größerer Entfernung

Dadurch laufen mehrere Gegner nicht auf exakt derselben Linie.

## Dodge-System

Die KI prüft nur in ihren Reaktionsintervallen, ob ein Spielerprojektil von unten in ihre Hitbox-Bahn läuft. Das hält die CPU-Last klein und verhindert perfekte Reaktionen. Die Ausweichchance und Reaktionszeit hängen vom Archetyp ab. Elite-Gegner reagieren schneller und häufiger, schwere Gegner deutlich träger.

## Schwierigkeit

`EnemyManager` bildet aus Sternsystem-Schwierigkeit und Score einen dynamischen Faktor. Dieser beeinflusst unter anderem:

- maximale Gegnerzahl
- Spawnintervall
- Geschwindigkeit
- Feuerfrequenz
- Zielgenauigkeit
- Elite-Wahrscheinlichkeit
- Torpedonutzung

## Erweiterungen

Boss- und Wellenlogik sollte oberhalb des `EnemyManager` ergänzt werden. Ein Boss kann `EnemyBase` ableiten und eigene `movement`, `brain` oder `weapons`-Komponenten erhalten. Für Koop kann der Manager später statt eines einzelnen `player` eine Zielauswahl aus mehreren Spielern bekommen, ohne die Projektil- oder Spawnklassen neu zu schreiben.
