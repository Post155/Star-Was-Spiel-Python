# Unity-Einrichtung

## Version und Pakete

| Punkt | Wert |
|---|---|
| Editor | 6000.6.6f1 (aus dem bereitgestellten Projekt übernommen) |
| Scripting | .NET Standard 2.1, C# 9 (Sim-Code verwendet nur C# 9, keine `init`/Records) |
| Pakete (neu) | `com.unity.ugui 2.0.0` – wird für das gesamte UI benötigt. Die mitgelieferte `manifest.json` enthält es; `packages-lock.json` wurde entfernt, damit Unity neu auflöst. |
| Pakete (vorhanden) | IDE-Pakete, alle `com.unity.modules.*`. `com.unity.test-framework` wird über das Visual-Studio-IDE-Paket mitgezogen (für den Test Runner). |
| Eingabe | **Active Input Handling = Input Manager (Old)** (Projekteinstellung bleibt unverändert). „Both“ funktioniert ebenfalls. Reines „Input System Package“ wird **nicht** unterstützt (der Code nutzt `UnityEngine.Input`). |

> Falls eure Unity-Version uGUI bereits eingebaut mitliefert und der Package Manager `com.unity.ugui` bemängelt, die Zeile in `Packages/manifest.json` entfernen. Diese Annahme konnte ohne Editor nicht geprüft werden.

## Architektur in Unity

* `StarWars.Sim` (asmdef, `noEngineReferences`): gesamte Spielregel-Logik, Netzwerk, Speichern, Inventar, Quests.
* Der Rest (`Scripts/Game`, `Scripts/Editor`) hat bewusst **keine** asmdef und landet in `Assembly-CSharp`, damit uGUI automatisch referenziert wird – unabhängig davon, wie die Assembly in der jeweiligen Unity-Version heißt.
* `Assets/Tests/EditMode` hat eine eigene asmdef (nur Editor, referenziert `StarWars.Sim` + NUnit).

## Szenen

Alle Szenen enthalten nur *Main Camera* + *SceneBootstrap*. Der Bootstrap baut anhand des Szenennamens Menü/Spiel/UI auf (uGUI-Canvas, Kameras, Sprite-Pools). Dadurch sind keine Inspector-Referenzen zu setzen.

| Szene | Inhalt |
|---|---|
| MainMenu | Hauptmenü, Rekord, Quests & Inventar |
| FactionSelection / DifficultySelection / ShipSelection | Auswahlfluss (lokal: je Spieler; LAN: nach Start-Anforderung) |
| Singleplayer | Einzelspieler + Game-Over-Dialog |
| MultiplayerMenu | Lokal/LAN, Regelwahl, LAN-Formular (Name, IP) |
| LocalPointsFight / LocalLastSurvivor | lokale Modi |
| LanLobby / LanGame | Lobby, Countdown, LAN-Spiel (Punktekampf oder Duell) |

Die Szenen sind in den Build Settings eingetragen (`ProjectSettings/EditorBuildSettings.asset`).

## Prefabs

`Assets/Resources/Prefabs/Pool_<name>.prefab` (19 Stück): jeweils GameObject + SpriteRenderer. Die Sprite-Pools instanziieren sie, wenn vorhanden (sonst wird ein GameObject per Code erzeugt). Damit lassen sich Material, Sorting Layer oder Shader pro Objekttyp zentral ändern.

## ScriptableObjects

`Assets/Resources/Content/…` (Menü *Star Wars → ScriptableObject-Daten exportieren*): Items werden zur Laufzeit geladen (überschreiben gleichnamige Standard-Items). Schiffe, Gegner-Archetypen und Sternensysteme werden als **Inspektions-Assets** exportiert; die Spielwerte bleiben im getesteten Sim-Code die einzige Wahrheitsquelle (Begründung: `MIGRATION_PLAN.md`).

## Grafiken

* Import: Sprite (Single), Pixels Per Unit **1**, Filter **Point**, keine Mipmaps, unkomprimiert, Alpha ist Transparenz. Der Code erzeugt die Sprites zusätzlich selbst aus der Texture2D und setzt Point-Filter – er hängt also nicht von den Import-Einstellungen ab.
* Planet „Sternzerstörer“ wurde zu ASCII `Sternzerstoerer.png` umbenannt; das im ZIP des Vorgängerports enthaltene Duplikat mit kaputtem Dateinamen entfällt.
* Fehlende Bilder werden als magentafarbenes Quadrat dargestellt (plus Warnung im Log) statt als leeres Objekt.

## Audio

Das Original enthält **keine** Audiodateien. `SoundBank` synthetisiert einfache Effekte zur Laufzeit (Laser, Torpedo, Explosion, Treffer, Warnung, Klick). Eigene Clips unter `Resources/Audio/<laser|torpedo|explosion|hit|warning|click>` haben Vorrang. Die Lautstärke läuft über `AudioListener.volume` (Einstellung wird gespeichert); ein AudioMixer-Asset wurde nicht angelegt.

## Speicherort

`Application.persistentDataPath/savegame.json` (+ `.bak`, bei Beschädigung `.corrupt`). Ein vorhandenes altes `highscore.json` (`{"highscore": N}`) im selben Ordner wird einmalig importiert.

## Eigenes Build

*File → Build Profiles* (bzw. Build Settings) → Szenen sind eingetragen → Windows/macOS/Linux Standalone. Für LAN-Tests mit zwei Instanzen den Build neben dem Editor starten.
