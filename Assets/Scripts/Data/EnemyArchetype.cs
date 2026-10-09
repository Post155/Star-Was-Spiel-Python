using UnityEngine;

namespace StarWarsUnity
{
    [CreateAssetMenu(menuName = "Star Wars/Enemy Archetype")]
    public sealed class EnemyArchetype : ScriptableObject
    {
        public string key;
        public string displayName;
        public int maxHp;
        public float maxSpeed;
        public float acceleration;
        [Range(0f, 1f)] public float armorResistance;
        public int laserDamage;
        public Vector2 laserCooldown = new Vector2(1.1f, 1.75f);
        public Vector2Int burstRange = new Vector2Int(1, 2);
        [Range(0f, 1f)] public float accuracy;
        public Vector2 reactionTime = new Vector2(0.26f, 0.48f);
        [Range(0f, 1f)] public float dodgeChance;
        public int torpedoDamage = 2;
        public Vector2 torpedoCooldown = new Vector2(10f, 14f);
        [Range(0f, 1f)] public float torpedoChance;
        public int baseScore;
        public Vector2Int bonusScore = new Vector2Int(0, 45);
        public float visualScaleMultiplier = 1f;
    }
}
