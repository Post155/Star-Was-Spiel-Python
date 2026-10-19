using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>game/enemies/config.py – EnemyArchetype (veränderbar, damit Balancing eine Kopie anpassen kann).</summary>
    public sealed class EnemyArchetype
    {
        public string Key, DisplayName;
        public int MaxHp;
        public double MaxSpeed, Acceleration, ArmorResistance;
        public int LaserDamage;
        public double LaserCooldownMin, LaserCooldownMax;
        public int BurstMin, BurstMax;
        public double Accuracy, ReactionMin, ReactionMax, DodgeChance;
        public int TorpedoDamage;
        public double TorpedoCooldownMin, TorpedoCooldownMax, TorpedoChance;
        public int BaseScore, BonusMin, BonusMax;
        public double VisualScaleMultiplier = 1.0;

        public EnemyArchetype Clone() => (EnemyArchetype)MemberwiseClone();
    }

    public static class EnemyArchetypes
    {
        public static readonly Dictionary<string, EnemyArchetype> All = new Dictionary<string, EnemyArchetype>
        {
            { "standard", new EnemyArchetype { Key = "standard", DisplayName = "STANDARD", MaxHp = 4, MaxSpeed = 185.0, Acceleration = 520.0, ArmorResistance = 0.00,
                LaserDamage = 1, LaserCooldownMin = 1.10, LaserCooldownMax = 1.75, BurstMin = 1, BurstMax = 2, Accuracy = 0.68, ReactionMin = 0.26, ReactionMax = 0.48, DodgeChance = 0.36,
                TorpedoDamage = 2, TorpedoCooldownMin = 10.0, TorpedoCooldownMax = 14.0, TorpedoChance = 0.14, BaseScore = 100, BonusMin = 0, BonusMax = 45 } },
            { "fast", new EnemyArchetype { Key = "fast", DisplayName = "SCHNELL", MaxHp = 3, MaxSpeed = 285.0, Acceleration = 760.0, ArmorResistance = 0.00,
                LaserDamage = 1, LaserCooldownMin = 0.78, LaserCooldownMax = 1.30, BurstMin = 1, BurstMax = 3, Accuracy = 0.61, ReactionMin = 0.16, ReactionMax = 0.31, DodgeChance = 0.58,
                TorpedoDamage = 2, TorpedoCooldownMin = 9.0, TorpedoCooldownMax = 13.0, TorpedoChance = 0.18, BaseScore = 190, BonusMin = 25, BonusMax = 90, VisualScaleMultiplier = 0.88 } },
            { "heavy", new EnemyArchetype { Key = "heavy", DisplayName = "SCHWER", MaxHp = 10, MaxSpeed = 125.0, Acceleration = 310.0, ArmorResistance = 0.28,
                LaserDamage = 2, LaserCooldownMin = 1.20, LaserCooldownMax = 1.85, BurstMin = 2, BurstMax = 3, Accuracy = 0.74, ReactionMin = 0.38, ReactionMax = 0.62, DodgeChance = 0.22,
                TorpedoDamage = 2, TorpedoCooldownMin = 8.0, TorpedoCooldownMax = 11.5, TorpedoChance = 0.34, BaseScore = 340, BonusMin = 55, BonusMax = 160, VisualScaleMultiplier = 1.18 } },
            { "elite", new EnemyArchetype { Key = "elite", DisplayName = "ELITE", MaxHp = 8, MaxSpeed = 250.0, Acceleration = 680.0, ArmorResistance = 0.14,
                LaserDamage = 2, LaserCooldownMin = 0.58, LaserCooldownMax = 0.96, BurstMin = 2, BurstMax = 4, Accuracy = 0.91, ReactionMin = 0.10, ReactionMax = 0.20, DodgeChance = 0.84,
                TorpedoDamage = 2, TorpedoCooldownMin = 5.8, TorpedoCooldownMax = 8.4, TorpedoChance = 0.58, BaseScore = 650, BonusMin = 110, BonusMax = 320, VisualScaleMultiplier = 1.05 } },
        };
    }
}
