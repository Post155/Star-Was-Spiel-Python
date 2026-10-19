using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace StarWars.Sim
{
    public sealed class GameSettings
    {
        public double MasterVolume = 0.8;
        public string LastDifficulty = "normal", LastShip = "xwing", LastFaction = "rebels", PlayerName = "Spieler";
    }

    /// <summary>Persistente Daten (versioniert). Highscore entspricht game/highscore.json des Originals.</summary>
    public sealed class SaveData
    {
        public const int CurrentVersion = 1;
        public int Version = CurrentVersion;
        public int Highscore;
        public GameSettings Settings = new GameSettings();
        public List<object> Inventory = new List<object>();
        public Dictionary<string, object> Quests = new Dictionary<string, object>();
        public int GamesPlayed;
    }

    public enum LoadStatus { Fresh, Loaded, RecoveredFromBackup, CorruptReset, Migrated }

    /// <summary>
    /// Robustes Speichern: atomares Schreiben (temp + Austausch), .bak-Sicherung, Wiederherstellung bei beschädigten
    /// Dateien, Migration älterer Dateien (inkl. altes {"highscore": N}-Format) und Versionsprüfung.
    /// </summary>
    public sealed class SaveService
    {
        private readonly string _dir;
        public string FilePath => Path.Combine(_dir, "savegame.json");
        public string BackupPath => FilePath + ".bak";
        public string LegacyHighscorePath => Path.Combine(_dir, "highscore.json");
        public SaveData Data { get; private set; } = new SaveData();
        public LoadStatus LastLoadStatus { get; private set; } = LoadStatus.Fresh;

        public SaveService(string directory) { _dir = directory; }

        public LoadStatus Load()
        {
            Directory.CreateDirectory(_dir);
            if (TryRead(FilePath, out var data, out bool migrated)) { Data = data; return LastLoadStatus = migrated ? LoadStatus.Migrated : LoadStatus.Loaded; }
            bool existed = File.Exists(FilePath);
            if (existed)
            {
                try { File.Copy(FilePath, FilePath + ".corrupt", true); } catch (Exception) { }
                if (TryRead(BackupPath, out var backup, out _)) { Data = backup; Save(); return LastLoadStatus = LoadStatus.RecoveredFromBackup; }
                Data = new SaveData(); ImportLegacyHighscore(); return LastLoadStatus = LoadStatus.CorruptReset;
            }
            Data = new SaveData();
            ImportLegacyHighscore();
            return LastLoadStatus = LoadStatus.Fresh;
        }

        private void ImportLegacyHighscore()
        {
            try
            {
                if (!File.Exists(LegacyHighscorePath)) return;
                if (Json.Parse(File.ReadAllText(LegacyHighscorePath, Encoding.UTF8)) is Dictionary<string, object> d)
                    Data.Highscore = (int)Json.Int(d, "highscore", 0, 0, int.MaxValue);
            }
            catch (Exception) { }
        }

        private static bool TryRead(string path, out SaveData data, out bool migrated)
        {
            data = null; migrated = false;
            try
            {
                if (!File.Exists(path)) return false;
                if (!(Json.Parse(File.ReadAllText(path, Encoding.UTF8)) is Dictionary<string, object> d)) return false;
                int version = (int)Json.Int(d, "version", 0);
                if (version > SaveData.CurrentVersion) return false;      // aus der Zukunft: nicht überschreiben/interpretieren
                var s = new SaveData { Version = SaveData.CurrentVersion };
                if (version < SaveData.CurrentVersion) migrated = true;
                s.Highscore = (int)Json.Int(d, "highscore", 0, 0, int.MaxValue);
                s.GamesPlayed = (int)Json.Int(d, "games_played", 0, 0, int.MaxValue);
                var st = Json.Obj(d, "settings");
                if (st != null)
                {
                    s.Settings.MasterVolume = Json.Num(st, "master_volume", 0.8, 0, 1);
                    string diff = Json.Str(st, "last_difficulty", "normal"); s.Settings.LastDifficulty = Difficulties.IsValid(diff) ? diff : "normal";
                    string ship = Json.Str(st, "last_ship", "xwing"); s.Settings.LastShip = ShipCatalog.IsValid(ship) ? ship : "xwing";
                    string fac = Json.Str(st, "last_faction", "rebels"); s.Settings.LastFaction = fac == "empire" ? "empire" : "rebels";
                    s.Settings.PlayerName = Proto.SafeName(Json.Str(st, "player_name", "Spieler"));
                }
                s.Inventory = Json.Arr(d, "inventory") ?? new List<object>();
                s.Quests = Json.Obj(d, "quests") ?? new Dictionary<string, object>();
                data = s; return true;
            }
            catch (Exception) { return false; }
        }

        public bool Save()
        {
            try
            {
                Directory.CreateDirectory(_dir);
                var d = new Dictionary<string, object>
                {
                    { "version", (long)SaveData.CurrentVersion }, { "highscore", (long)Data.Highscore }, { "games_played", (long)Data.GamesPlayed },
                    { "settings", new Dictionary<string, object> { { "master_volume", Data.Settings.MasterVolume }, { "last_difficulty", Data.Settings.LastDifficulty }, { "last_ship", Data.Settings.LastShip }, { "last_faction", Data.Settings.LastFaction }, { "player_name", Data.Settings.PlayerName } } },
                    { "inventory", Data.Inventory }, { "quests", Data.Quests },
                };
                string tmp = FilePath + ".tmp";
                File.WriteAllText(tmp, Json.Serialize(d, true), new UTF8Encoding(false));
                if (File.Exists(FilePath)) { try { File.Copy(FilePath, BackupPath, true); } catch (Exception) { } }
                if (File.Exists(FilePath)) File.Delete(FilePath);
                File.Move(tmp, FilePath);
                return true;
            }
            catch (Exception) { return false; }
        }

        /// <summary>Verhalten von death_screen im Original: neuer Rekord wird gespeichert. Gibt true bei neuem Rekord zurück.</summary>
        public bool SubmitScore(int score)
        {
            Data.GamesPlayed++;
            bool record = score > Data.Highscore;
            if (record) Data.Highscore = score;
            Save();
            return record;
        }
    }
}
