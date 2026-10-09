using System;
using System.Collections.Generic;

namespace StarWarsUnity
{
    [Serializable]
    public sealed class SaveGameData
    {
        public int score;
        public string difficulty = "normal";
        public string ship = "XWing";
        public List<InventorySlot> inventory = new List<InventorySlot>();
        public List<QuestState> quests = new List<QuestState>();
        public string currentSystem = "EARTH";
        public int systemIndex;
    }
}
