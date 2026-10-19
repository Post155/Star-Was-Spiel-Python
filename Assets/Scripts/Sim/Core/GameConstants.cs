using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>1:1-Übernahme von game/constants.py (maßgebliche Quelle; die README des Originals nennt teils abweichende Beispielwerte).</summary>
    public static class GameConstants
    {
        public const int Width = 800, Height = 600;
        public const string ScreenTitle = "Star Wars";
        public const int TicksPerSecond = 60;
        public const double TickSeconds = 1.0 / 60.0;
        public const double TickMs = 1000.0 / 60.0;

        public const int AsteroidSpawnInterval = 60;
        public const int AsteroidMinSpawnInterval = 22;
        public const int AsteroidSpeedMin = 2, AsteroidSpeedMax = 8;

        public const int SystemSwitchPoints = 2000;
        public const int SystemSwitchTimeMs = 30000;
        public const int GalaxyMapDurationMs = 5000;
        public const int HyperspaceDurationMs = 14000;
        public const int SystemEntryDelayMs = 10000;   // BackgroundManager.system_entry_delay_ms
        public const int SystemExitDelayMs = 10000;    // BackgroundManager.system_exit_delay_ms

        public const int PlayerBaseSpeed = 10;
        public const int ShipSpeedXWing = 12, ShipSpeedMillennium = 14, ShipSpeedTieFighter = 11, ShipSpeedBattleDroid = 12;
        public const int ShipReferenceSize = 96;
        public const int PlayerLives = 3;
        public const int InvulnerableDurationMs = 2000;
        public const int InvulnerableBlinkMs = 200;

        public const int EnemyUnlockStandardPoints = 2000;
        public const int EnemyUnlockHeavyPoints = 5000;
        public const int EnemyUnlockElitePoints = 10000;
        public static readonly double[] SystemDifficultyBonus = { 0.00, 0.15, 0.30, 0.50 };
        public const double SystemProgressMaxBonus = 0.20;
        public const int EnemyWarningDurationMs = 2500;

        // PvP-Duell
        public const int PvpMaxPlayers = 2;
        public const int PvpStartCountdownMs = 3000;
        public const int PvpSnapshotIntervalMs = 50;
        public const int PvpInputIntervalMs = 50;
        public const int PvpRespawnDelayMs = 900;
        public const int PvpRespawnInvulnerabilityMs = 2000;
        public const int PvpPlayerTopMargin = 28, PvpPlayerBottomMargin = 28;
        public const int PvpAsteroidPlayerSafeDistance = 130;
        public const int PvpAsteroidSpawnAttempts = 80;
        public const int PvpAsteroidBaseSpawnInterval = 55;
        public const int PvpAsteroidMinSpawnInterval = 20;
        public const int PvpAsteroidMax = 36;
        public const int PvpPlayerSpeed = 12;
        public const int PvpLaserDamage = 1, PvpTorpedoDamage = 2;
        public const int PvpHitScore = 150, PvpKillScore = 1000;
        public const int PvpMaxProjectiles = 80;
        public const int PvpScoreLimitMs = 180000;
        public const int PvpExplosionDurationMs = 500;
        public const int PvpResultDelayMs = 1600;
        public const string PvpDefaultMode = "last_survivor";

        // Netzwerk (game/network.py)
        public const int LanPort = 48732;
        public const int ProtocolVersion = 1;
        public const int MaxPlayers = 10;
        public const double StateBroadcastIntervalSec = 0.05;
        public const int MaxLineBytes = 16384;
        public const int MaxNameLength = 20;

        public const string DefaultDifficulty = "normal";
        public const string LocalPlayer1Name = "Spieler 1";
        public const string LocalPlayer2Name = "Spieler 2";
    }

    /// <summary>Ein Eintrag aus DIFFICULTY_SETTINGS.</summary>
    public sealed class DifficultyProfile
    {
        public string Key, Name;
        public double EnemyAccuracy, EnemyHp, EnemySpeed, EnemyAggression, EnemyMax, EnemySpawn, AsteroidDensity, AsteroidSpeed, AsteroidSize;
        public string Description;
    }

    public static class Difficulties
    {
        public static readonly string[] Keys = { "easy", "normal", "hard", "expert" };

        private static readonly Dictionary<string, DifficultyProfile> Table = new Dictionary<string, DifficultyProfile>
        {
            { "easy",   new DifficultyProfile { Key = "easy",   Name = "Einfach", Description = "Weniger und langsamere Gegner",
                EnemyAccuracy = 0.72, EnemyHp = 0.80, EnemySpeed = 0.82, EnemyAggression = 0.70, EnemyMax = 0.65, EnemySpawn = 1.25, AsteroidDensity = 0.78, AsteroidSpeed = 0.82, AsteroidSize = 0.90 } },
            { "normal", new DifficultyProfile { Key = "normal", Name = "Normal", Description = "Ausgewogene Herausforderung",
                EnemyAccuracy = 0.90, EnemyHp = 1.00, EnemySpeed = 0.95, EnemyAggression = 0.88, EnemyMax = 0.82, EnemySpawn = 1.10, AsteroidDensity = 0.90, AsteroidSpeed = 0.92, AsteroidSize = 0.95 } },
            { "hard",   new DifficultyProfile { Key = "hard",   Name = "Schwer", Description = "Stärkere und aggressivere Gegner",
                EnemyAccuracy = 1.00, EnemyHp = 1.12, EnemySpeed = 1.05, EnemyAggression = 1.05, EnemyMax = 1.00, EnemySpawn = 0.92, AsteroidDensity = 1.05, AsteroidSpeed = 1.05, AsteroidSize = 1.00 } },
            { "expert", new DifficultyProfile { Key = "expert", Name = "Experte", Description = "Für erfahrene Spieler",
                EnemyAccuracy = 1.08, EnemyHp = 1.25, EnemySpeed = 1.14, EnemyAggression = 1.20, EnemyMax = 1.15, EnemySpawn = 0.80, AsteroidDensity = 1.18, AsteroidSpeed = 1.15, AsteroidSize = 1.08 } },
        };

        public static bool IsValid(string key) => key != null && Table.ContainsKey(key);
        public static DifficultyProfile Get(string key) => IsValid(key) ? Table[key] : Table[GameConstants.DefaultDifficulty];

        public static double SystemBonus(int systemIndex)
        {
            int idx = Math.Max(0, systemIndex);
            var t = GameConstants.SystemDifficultyBonus;
            return idx < t.Length ? t[idx] : t[t.Length - 1];
        }
    }
}
