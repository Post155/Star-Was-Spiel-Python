using UnityEngine;

namespace StarWarsUnity
{
    public enum ShipId { XWing, MillenniumFalcon, TieFighter, BattleDroid }
    public enum Faction { Rebels, Empire }

    [CreateAssetMenu(menuName = "Star Wars/Ship Definition")]
    public sealed class ShipDefinition : ScriptableObject
    {
        public ShipId id;
        public string displayName;
        public Faction faction;
        public Sprite sprite;
        public Sprite torpedoSprite;
        public float moveSpeed;
        [Range(0.1f, 2f)] public float scale = 1f;
        public bool canFireTorpedo;
        public Vector2[] laserMuzzles;
        public Vector2 torpedoMuzzle;
    }
}
