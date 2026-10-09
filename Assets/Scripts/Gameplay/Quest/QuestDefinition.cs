using UnityEngine;

namespace StarWarsUnity
{
    [CreateAssetMenu(menuName = "Star Wars/Quest")]
    public sealed class QuestDefinition : ScriptableObject
    {
        public string questId;
        public string title;
        [TextArea] public string description;
        public int requiredValue = 1;
        public int scoreReward;
        public ItemDefinition rewardItem;
        public int rewardAmount = 1;
    }
}
