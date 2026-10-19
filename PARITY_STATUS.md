# Paritätsstatus

Legende: ✅ portiert **und** automatisiert gegen das Original/Regeln getestet (Sim-Schicht) · 🟡 portiert, aber nur kompiliert – **nicht in Unity ausgeführt** · 🆕 neu (kein Original) · ⬜ nicht portiert · ⚠️ bewusst abweichend (siehe Spalte)

## Gameplay

| Bereich | Status | Anmerkung |
|---|---|---|
| Schiffe X-Wing, Falcon, TIE, Battle Droid (Tempo, Größe, Hitbox, Laser, Torpedo) | ✅ | Golden-Test gegen Python |
| Spielerbewegung, Grenzen, Leben, Unverwundbarkeit, Blinken | ✅ | |
| Laser/Torpedo, Schaden (1/4), Rüstung | ✅ | |
| Asteroiden (Spawn, Größe, Tempo, Animation, Kollision, Punkte) | ✅ | Spawn im festen 60-Hz-Takt |
| Gegner-KI (Brain, Movement, Weapons, Archetypen, Rollen, Ausweichen, Zielvorhersage) | ✅ | Movement exakt per Golden; Zufallsanteile statistisch geprüft |
| Gegner-Manager (Freischaltung, Warnungen, Intervalle, Limits, Balancing) | ✅ | 312 Kombinationen exakt |
| Schwierigkeitsgrade (4 Stufen, 9 Parameter) | ✅ | |
| Sternensysteme (12, Reihenfolge, Wechsel 2000 Punkte/30 s, Planetenfenster, Systembonus) | ✅ | Logik; Darstellung 🟡 |
| Sterne/Parallax/Vordergrund-Silhouetten | ✅ Logik / 🟡 Darstellung | |
| Karten-Überblendung beim Systemwechsel | 🟡 ⚠️ | vereinfachte Darstellung (siehe unten) |
| Hyperspace-Animation (14 s) | ⬜ | im Original nur im Sync-Code erwähnt, im Spiel nicht angezeigt |
| Punkte, Highscore (persönlicher Rekord) | ✅ Logik / 🟡 Dialog | kein Leaderboard (gibt es im Original nicht) |
| HUD (Punkte, Leben als Lichtschwerter, Warn-Overlay, Systemanzeige) | 🟡 ⚠️ | Layout/Schrift an uGUI angepasst |

## Modi

| Modus | Status | Anmerkung |
|---|---|---|
| Einzelspieler (Menüfluss + Spiel + Game Over) | ✅ Simulation / 🟡 Menüs, Rendering | |
| Lokaler Punktekampf (2 getrennte Welten, 180 s, TAB, Ghost) | ✅ Simulation / 🟡 Darstellung | Original-Bug (Asteroidentempo) korrigiert |
| Lokaler Letzter Überlebender | ✅ Simulation / 🟡 Darstellung | |
| LAN-Lobby (Host, Beitritt per IP, Bereit, Countdown, Start) | ✅ (echte Sockets) / 🟡 Lobby-UI | |
| LAN-PvP (Host-autoritativ) | ✅ Treiberebene / 🟡 Darstellung | nicht mit zwei Unity-Prozessen erprobt |
| LAN-Punktekampf (≤ 10 Spieler, Ghosts, Rangliste) | ✅ Netzebene / 🟡 Spiel + UI | |
| Verbindungsabbruch/Host-Ende/Müll/Übergröße | ✅ | |

## Systeme

| System | Status |
|---|---|
| Speichersystem (Rekord, Einstellungen, Auswahl, Inventar, Quests; Backup/Korruption/Migration) | 🆕 ✅ |
| Inventar, Items | 🆕 ✅ (Logik) / 🟡 Anzeige (Textliste im Hauptmenü) |
| Questsystem | 🆕 ✅ (Logik) / 🟡 Anzeige + Anbindung an Einzelspieler-Ereignisse |
| CombatSystem (Rüstungsformel, Treffer-Ledger) | 🆕 ✅ |
| Audio | 🆕 🟡 (Original hatte keines; synthetisierte Effekte, kein AudioMixer-Asset) |
| ScriptableObjects | 🆕 🟡 (Items laufzeitrelevant, übrige als Inspektions-Export) |

## Unity-Projekt

| Bereich | Status |
|---|---|
| 10 Szenen + Build Settings | 🟡 handgeschrieben, YAML geprüft, nicht von Unity geladen |
| 19 Pool-Prefabs | 🟡 dito |
| Pixelart-Import (Sprite, Point, PPU 1) | 🟡 .meta angepasst + Code-seitige Absicherung + Reparaturmenü |
| Paketliste (`com.unity.ugui`) | 🟡 Annahme, siehe UNITY_SETUP |
| Editor-Menü „Star Wars“ | 🟡 gegen API-Nachbildung kompiliert |
| EditMode-Tests (Unity Test Runner) | 🟡 gegen echte NUnit-DLL kompiliert, nicht im Editor ausgeführt |

## Bewusste Abweichungen vom Original

| # | Original | Port | Grund |
|---|---|---|---|
| 1 | Fenster beliebig skalierbar, Spielfeld wächst mit | Logische Fläche 800×600 mit Letterbox | gleiche Spielbalance auf jeder Auflösung |
| 2 | Lane-Asteroiden im PvP: Entfernungsprüfung durch doppelte Methode verdeckt | Beabsichtigte Prüfung | Leck/Blockade der Asteroidenobergrenze |
| 3 | Punktekampf-Asteroidentempo ohne Wirkung (Attributfehler) | Multiplikator wirkt | Konsistenz mit Einzelspieler |
| 4 | Countdown nur per Epoch-Zeit | zusätzlich `remaining_ms` | Uhrenabweichung zwischen Rechnern |
| 5 | LAN-Host = erster Verbundener | Host = Loopback-Verbindung des Erstellers | Wettlauf (Test) |
| 6 | PvP-Eingaben ohne Validierung | Sequenz-/Raten-/Phasenprüfung | Anforderung „Eingaben validieren“ |
| 7 | Flash additives Weiß | Rot-Tönung | Unity-Sprite-Shader kennt kein additives Aufhellen ohne eigenes Material |
| 8 | Ghost-Skalierungstabelle | Ghost = tatsächliche Schiffsgröße | Tabelle nicht eindeutig auf die Schiffsmaße anwendbar |
| 9 | Karten-Überblendung (Thumbnails, Kartenzeichnung) | Dimmung + Linie + Kreise + Namen + 1 Thumbnail | Aufwand/Test ohne Editor |
| 10 | Esc im Schwierigkeitsmenü liefert die Auswahl | Esc geht zurück | sinnvollere Bedienung |
| 11 | Zeitquelle `pygame.time.get_ticks()` | Simulationsuhr pro Welt | Determinismus/Tests |

## Offen / Risiken

1. **Kein Unity-Lauf.** Compilerfehler, die nur das echte Unity bemängelt (z. B. API-Unterschiede in 6000.6), sind möglich. Der Sim-Teil (reines C#) ist davon nicht betroffen.
2. **uGUI-Paket:** Die Annahme `com.unity.ugui 2.0.0` konnte nicht geprüft werden (siehe `UNITY_SETUP.md`).
3. **Layout/Optik:** Alle UI-Positionen, Schriftgrößen, Sortierreihenfolgen und die Torpedo-Ausrichtung der Gegner sind ungetestet; Feinschliff nach dem ersten Start ist wahrscheinlich.
4. **Szenen/Prefabs** wurden als YAML geschrieben; falls Unity sie beim Import beanstandet, stellt *Star Wars → 1) Alles einrichten* sie über die Unity-API her.
5. **LAN mit zwei Unity-Instanzen** und Firewall-Verhalten ungetestet; Interpolation des Clients (Faktor 0,35 pro Tick) nur an der Logik geprüft.
6. **Original-Schriftarten/Menütexte** wurden nicht 1:1 nachgebaut (nur Texte und Abläufe).
7. **Quests/Inventar** sind funktionierende, aber bewusst schlanke Systeme ohne eigene Spielwelt-Integration (keine Item-Verwendung im Kampf).
8. **Kein AudioMixer-Asset**, keine Original-Sounds (existieren nicht).
