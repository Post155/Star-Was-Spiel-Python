using System;
using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    [Serializable]
    public sealed class InventorySlot
    {
        public string itemId;
        public int amount;
    }

    public sealed class InventorySystem : MonoBehaviour
    {
        [SerializeField] private int capacity = 24;
        [SerializeField] private List<InventorySlot> slots = new List<InventorySlot>();
        public IReadOnlyList<InventorySlot> Slots => slots;
        public event Action Changed;

        public bool Add(ItemDefinition item, int amount = 1)
        {
            if (item == null || amount <= 0) return false;
            var existing = slots.Find(s => s.itemId == item.itemId && s.amount < item.maxStack);
            while (amount > 0 && existing != null)
            {
                int add = Mathf.Min(amount, item.maxStack - existing.amount);
                existing.amount += add; amount -= add;
            }
            while (amount > 0 && slots.Count < capacity)
            {
                int add = Mathf.Min(amount, item.maxStack);
                slots.Add(new InventorySlot { itemId = item.itemId, amount = add });
                amount -= add;
            }
            Changed?.Invoke();
            return amount == 0;
        }

        public bool Remove(string itemId, int amount = 1)
        {
            for (int i=slots.Count-1;i>=0 && amount>0;i--)
            {
                if (slots[i].itemId != itemId) continue;
                int taken = Mathf.Min(amount, slots[i].amount);
                slots[i].amount -= taken; amount -= taken;
                if (slots[i].amount <= 0) slots.RemoveAt(i);
            }
            Changed?.Invoke();
            return amount == 0;
        }

        public int Count(string itemId)
        {
            int total=0; foreach(var s in slots) if(s.itemId==itemId) total+=s.amount; return total;
        }

        public void Clear(){slots.Clear();Changed?.Invoke();}
    }
}
