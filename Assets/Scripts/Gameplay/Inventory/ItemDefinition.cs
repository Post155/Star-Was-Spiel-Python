using UnityEngine;

namespace StarWarsUnity
{
    public enum ItemType { Consumable, Weapon, Equipment, QuestItem, Cargo }

    [CreateAssetMenu(menuName = "Star Wars/Item Definition")]
    public sealed class ItemDefinition : ScriptableObject
    {
        public string itemId;
        public string displayName;
        public ItemType type;
        [TextArea] public string description;
        [Min(1)] public int maxStack = 1;
        public Sprite icon;
        public int value;
    }
}
