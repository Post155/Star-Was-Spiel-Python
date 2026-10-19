# Werkzeuge (Python, nur für die Neuerzeugung von Daten)

| Datei | Zweck |
|---|---|
| `extract_metrics.py` | Liest mit **echtem Pygame** aus dem Original: Sprite-Größen, Alpha-Hitboxen, Gegner-Metriken, Planeten-Dateien. Ergebnis: `metrics.json`. |
| `gen_metrics_cs.py` | Erzeugt daraus `Assets/Scripts/Sim/Data/AssetMetrics.cs`. |
| `gen_golden.py` | Führt deterministische Funktionen des **Original-Pythoncodes** aus und schreibt `Tests/Golden/golden.json` (Referenz für die C#-Tests). |
| `generate_unity_files.py` | Erzeugt `.meta`-Dateien (stabile GUIDs), Szenen, Prefabs, Build Settings, Paketliste. Wiederholbar. |

Die Skripte erwarten das Original unter `/home/claude/work/py/Star-Was-Spiel-Python` (Pfade oben in den Dateien anpassen). Für den normalen Unity-Betrieb werden sie nicht benötigt.
