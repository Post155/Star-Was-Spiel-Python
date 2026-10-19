using UnityEngine;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>
    /// ScriptableObject-Datenassets. Gegenstände werden zur Laufzeit aus Resources/Content/Items geladen (ItemDatabase);
    /// fehlen sie, gelten die Standard-Items aus dem Code. Schiffe, Gegner-Archetypen und Sternensysteme existieren als
    /// Inspektions-/Dokumentationsassets (Export aus den paritätsgeprüften Code-Katalogen): Die Spielwerte bleiben im
    /// Sim-Code die einzige Wahrheitsquelle, damit keine zwei widersprüchlichen Datenquellen entstehen.
    /// </summary>
    [CreateAssetMenu(menuName = "Star Wars/Item", fileName = "Item")]
    public sealed class ItemDefinitionAsset : ScriptableObject
    {
        public string id; public string displayName; [TextArea] public string description; public ItemType type; public Sprite icon; public int value; public int maxStack = 1;

        public ItemDefinition ToSim() => new ItemDefinition { Id = id, Name = displayName, Description = description, Type = type, Value = value, MaxStack = Mathf.Max(1, maxStack), IconKey = icon != null ? icon.name : "" };
    }

    [CreateAssetMenu(menuName = "Star Wars/Schiff (Info)", fileName = "Ship")]
    public sealed class ShipDefinitionAsset : ScriptableObject
    {
        public string key; public string displayName; public Faction faction; public int speed; public bool hasTorpedo; public int pixelWidth, pixelHeight, hitboxWidth, hitboxHeight; public Sprite sprite;
    }

    [CreateAssetMenu(menuName = "Star Wars/Gegner-Archetyp (Info)", fileName = "EnemyArchetype")]
    public sealed class EnemyArchetypeAsset : ScriptableObject
    {
        public string key, displayName; public int maxHp; public float maxSpeed, acceleration, armorResistance, accuracy, dodgeChance, torpedoChance; public int baseScore;
    }

    [CreateAssetMenu(menuName = "Star Wars/Sternensystem (Info)", fileName = "StarSystem")]
    public sealed class StarSystemAsset : ScriptableObject
    {
        public string idName; public string[] displayLines; public string[] planetKeys; public float starDensity, asteroidSpeedMultiplier; public int difficulty;
    }

    public static class ContentLoader
    {
        /// <summary>Standard-Items + (optional) Items aus Resources/Content/Items; ScriptableObjects überschreiben gleichnamige IDs.</summary>
        public static ItemDatabase LoadItems()
        {
            var db = ItemDatabase.CreateDefault();
            var assets = Resources.LoadAll<ItemDefinitionAsset>("Content/Items");
            foreach (var a in assets) if (a != null && !string.IsNullOrWhiteSpace(a.id)) db.Register(a.ToSim());
            return db;
        }
    }
}
