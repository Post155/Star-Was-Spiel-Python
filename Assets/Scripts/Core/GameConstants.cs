using UnityEngine;

namespace StarWarsUnity
{
    public static class GameConstants
    {
        public const int ReferenceWidth = 800;
        public const int ReferenceHeight = 600;
        public const string ScreenTitle = "Star Wars";

        public const float PlayerBaseSpeed = 10f;
        public const float ShipSpeedXWing = 12f;
        public const float ShipSpeedMillennium = 14f;
        public const float ShipSpeedTieFighter = 11f;
        public const float ShipSpeedBattleDroid = 12f;
        public const float ShipReferenceSize = 96f;

        public const int AsteroidSpawnIntervalFrames = 60;
        public const int AsteroidMinSpawnIntervalFrames = 22;
        public const float AsteroidMinSpeed = 2f;
        public const float AsteroidMaxSpeed = 8f;

        public const int SystemSwitchPoints = 2000;
        public const int SystemSwitchTimeMs = 30000;
        public const int HyperspaceDurationMs = 14000;
        public const int GalaxyMapDurationMs = 5000;
        public const int EnemyWarningDurationMs = 2500;

        public const int EnemyUnlockStandardPoints = 2000;
        public const int EnemyUnlockHeavyPoints = 5000;
        public const int EnemyUnlockElitePoints = 10000;
        public const float SystemProgressMaxBonus = 0.20f;

        public const int PvPMaxPlayers = 2;
        public const int PvPStartCountdownMs = 3000;
        public const int PvPSnapshotIntervalMs = 50;
        public const int PvPInputIntervalMs = 50;
        public const int PvPRespawnDelayMs = 900;
        public const int PvPRespawnInvulnerabilityMs = 2000;
        public const int PvPScoreLimitMs = 180000;
        public const float PvPPlayerSpeed = 12f;
        public const int PvPLaserDamage = 1;
        public const int PvPTorpedoDamage = 2;
        public const int PvPHitScore = 150;
        public const int PvPKillScore = 1000;

        public static readonly float[] SystemDifficultyBonus = { 0f, 0.15f, 0.30f, 0.50f };

        public static readonly DifficultyProfile Easy = new DifficultyProfile(
            "easy", "Einfach", 0.72f, 0.80f, 0.82f, 0.70f, 0.65f, 1.25f, 0.78f, 0.82f, 0.90f);
        public static readonly DifficultyProfile Normal = new DifficultyProfile(
            "normal", "Normal", 0.90f, 1.00f, 0.95f, 0.88f, 0.82f, 1.10f, 0.90f, 0.92f, 0.95f);
        public static readonly DifficultyProfile Hard = new DifficultyProfile(
            "hard", "Schwer", 1.00f, 1.12f, 1.05f, 1.05f, 1.00f, 0.92f, 1.05f, 1.05f, 1.00f);
        public static readonly DifficultyProfile Expert = new DifficultyProfile(
            "expert", "Experte", 1.08f, 1.25f, 1.14f, 1.20f, 1.15f, 0.80f, 1.18f, 1.15f, 1.08f);

        public static DifficultyProfile GetDifficulty(string key)
        {
            switch ((key ?? "normal").ToLowerInvariant())
            {
                case "easy": return Easy;
                case "hard": return Hard;
                case "expert": return Expert;
                default: return Normal;
            }
        }

        public static float GetSystemBonus(int systemIndex)
        {
            int index = Mathf.Max(0, systemIndex);
            return index < SystemDifficultyBonus.Length
                ? SystemDifficultyBonus[index]
                : SystemDifficultyBonus[SystemDifficultyBonus.Length - 1];
        }
    }

    public readonly struct DifficultyProfile
    {
        public readonly string Key;
        public readonly string DisplayName;
        public readonly float EnemyAccuracy;
        public readonly float EnemyHp;
        public readonly float EnemySpeed;
        public readonly float EnemyAggression;
        public readonly float EnemyMax;
        public readonly float EnemySpawn;
        public readonly float AsteroidDensity;
        public readonly float AsteroidSpeed;
        public readonly float AsteroidSize;

        public DifficultyProfile(string key, string displayName, float enemyAccuracy, float enemyHp,
            float enemySpeed, float enemyAggression, float enemyMax, float enemySpawn,
            float asteroidDensity, float asteroidSpeed, float asteroidSize)
        {
            Key = key;
            DisplayName = displayName;
            EnemyAccuracy = enemyAccuracy;
            EnemyHp = enemyHp;
            EnemySpeed = enemySpeed;
            EnemyAggression = enemyAggression;
            EnemyMax = enemyMax;
            EnemySpawn = enemySpawn;
            AsteroidDensity = asteroidDensity;
            AsteroidSpeed = asteroidSpeed;
            AsteroidSize = asteroidSize;
        }
    }
}
