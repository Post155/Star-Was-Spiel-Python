using System;
using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    [Serializable]
    public sealed class QuestState
    {
        public string questId;
        public int progress;
        public bool completed;
        public bool claimed;
    }

    public sealed class QuestSystem : MonoBehaviour
    {
        [SerializeField] private List<QuestState> active = new List<QuestState>();
        [SerializeField] private InventorySystem inventory;
        public IReadOnlyList<QuestState> Active => active;
        public event Action Changed;

        public void Track(QuestDefinition quest)
        {
            if (quest == null || active.Exists(q => q.questId == quest.questId)) return;
            active.Add(new QuestState { questId = quest.questId }); Changed?.Invoke();
        }

        public void AddProgress(QuestDefinition quest, int amount)
        {
            if (quest == null) return;
            Track(quest);
            var state = active.Find(q => q.questId == quest.questId);
            if (state.completed) return;
            state.progress = Mathf.Min(quest.requiredValue, state.progress + Mathf.Max(0, amount));
            if (state.progress >= quest.requiredValue) state.completed = true;
            Changed?.Invoke();
        }

        public bool Claim(QuestDefinition quest)
        {
            if (quest == null) return false;
            var state = active.Find(q => q.questId == quest.questId);
            if (state == null || !state.completed || state.claimed) return false;
            state.claimed = true;
            if (GameSession.Instance != null) GameSession.Instance.AddScore(quest.scoreReward);
            if (inventory != null && quest.rewardItem != null) inventory.Add(quest.rewardItem, quest.rewardAmount);
            Changed?.Invoke();
            return true;
        }
    }
}
