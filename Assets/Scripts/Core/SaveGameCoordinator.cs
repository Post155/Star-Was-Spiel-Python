using UnityEngine;

namespace StarWarsUnity
{
    public sealed class SaveGameCoordinator : MonoBehaviour
    {
        [SerializeField] private InventorySystem inventory;
        [SerializeField] private QuestSystem quests;

        public void SaveNow()
        {
            var data = new SaveGameData();
            if (GameSession.Instance != null)
            {
                data.score = GameSession.Instance.Score;
                data.difficulty = GameSession.Instance.Difficulty;
                data.ship = GameSession.Instance.SelectedShip.ToString();
            }
            if (inventory != null) data.inventory.AddRange(inventory.Slots);
            if (quests != null) data.quests.AddRange(quests.Active);
            SaveSystem.Save(data);
        }

        public SaveGameData Load() => SaveSystem.Load();
    }
}
