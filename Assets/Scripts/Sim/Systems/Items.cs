using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    public enum ItemType { Consumable, Equipment, Weapon, QuestItem, Cargo }

    /// <summary>Datengetriebene Gegenstandsdefinition (neues System – im Python-Original gab es keine Items).</summary>
    public sealed class ItemDefinition
    {
        public string Id, Name, Description, IconKey;
        public ItemType Type;
        public int Value;
        public int MaxStack = 1;
        public bool Stackable => MaxStack > 1;
    }

    public sealed class ItemDatabase
    {
        private readonly Dictionary<string, ItemDefinition> _items = new Dictionary<string, ItemDefinition>();

        public ItemDatabase() { }

        public static ItemDatabase CreateDefault()
        {
            var db = new ItemDatabase();
            db.Register(new ItemDefinition { Id = "repair_kit", Name = "Reparatursatz", Description = "Stellt Hüllenintegrität wieder her.", Type = ItemType.Consumable, Value = 150, MaxStack = 5, IconKey = "repair" });
            db.Register(new ItemDefinition { Id = "torpedo_crate", Name = "Torpedo-Kiste", Description = "Zusätzliche Protonentorpedos.", Type = ItemType.Weapon, Value = 200, MaxStack = 10, IconKey = "torpedo" });
            db.Register(new ItemDefinition { Id = "shield_booster", Name = "Schildverstärker", Description = "Verstärkt die Schilde des Schiffs.", Type = ItemType.Equipment, Value = 400, MaxStack = 1, IconKey = "shield" });
            db.Register(new ItemDefinition { Id = "kyber_crystal", Name = "Kyberkristall", Description = "Seltenes Kristall – Questgegenstand.", Type = ItemType.QuestItem, Value = 0, MaxStack = 3, IconKey = "kyber" });
            db.Register(new ItemDefinition { Id = "spice_cargo", Name = "Gewürzfracht", Description = "Wertvolle Handelsware.", Type = ItemType.Cargo, Value = 250, MaxStack = 20, IconKey = "cargo" });
            return db;
        }

        public void Register(ItemDefinition def)
        {
            if (def == null || string.IsNullOrWhiteSpace(def.Id)) throw new ArgumentException("Item braucht eine eindeutige ID.");
            if (def.MaxStack < 1) def.MaxStack = 1;
            _items[def.Id] = def;
        }

        public bool TryGet(string id, out ItemDefinition def) => _items.TryGetValue(id ?? "", out def);
        public ItemDefinition Get(string id) => _items.TryGetValue(id ?? "", out var d) ? d : null;
        public IEnumerable<ItemDefinition> All => _items.Values;
    }

    public struct InventorySlot
    {
        public string ItemId; public int Count;
        public bool IsEmpty => string.IsNullOrEmpty(ItemId) || Count <= 0;
    }

    /// <summary>Slot-Inventar mit Stapelgrößen, Kapazitätsgrenze und Änderungs-Ereignis (für UI-Aktualisierung).</summary>
    public sealed class Inventory
    {
        private readonly InventorySlot[] _slots;
        private readonly ItemDatabase _db;
        public event Action Changed;

        public Inventory(ItemDatabase db, int slotCount = 12)
        {
            if (slotCount < 1) throw new ArgumentOutOfRangeException(nameof(slotCount));
            _db = db; _slots = new InventorySlot[slotCount];
        }

        public int SlotCount => _slots.Length;
        public InventorySlot GetSlot(int i) => _slots[i];

        /// <summary>Fügt hinzu und liefert die Menge, die NICHT mehr hineinpasste (0 = alles eingelagert).</summary>
        public int Add(string itemId, int count)
        {
            if (count <= 0) return 0;
            if (!_db.TryGet(itemId, out var def)) return count;
            int remaining = count;
            for (int i = 0; i < _slots.Length && remaining > 0; i++)
            {
                if (_slots[i].ItemId != itemId || _slots[i].Count >= def.MaxStack) continue;
                int add = Math.Min(remaining, def.MaxStack - _slots[i].Count);
                _slots[i].Count += add; remaining -= add;
            }
            for (int i = 0; i < _slots.Length && remaining > 0; i++)
            {
                if (!_slots[i].IsEmpty) continue;
                int add = Math.Min(remaining, def.MaxStack);
                _slots[i] = new InventorySlot { ItemId = itemId, Count = add }; remaining -= add;
            }
            if (remaining != count) Changed?.Invoke();
            return remaining;
        }

        public int Count(string itemId) { int n = 0; foreach (var s in _slots) if (s.ItemId == itemId) n += s.Count; return n; }
        public bool Has(string itemId, int count = 1) => Count(itemId) >= count;

        /// <summary>Entfernt genau die Menge oder gar nichts (false, wenn zu wenig vorhanden).</summary>
        public bool Remove(string itemId, int count)
        {
            if (count <= 0) return true;
            if (Count(itemId) < count) return false;
            int remaining = count;
            for (int i = _slots.Length - 1; i >= 0 && remaining > 0; i--)
            {
                if (_slots[i].ItemId != itemId) continue;
                int take = Math.Min(remaining, _slots[i].Count);
                _slots[i].Count -= take; remaining -= take;
                if (_slots[i].Count <= 0) _slots[i] = default;
            }
            Changed?.Invoke();
            return true;
        }

        public int FreeSlots() { int n = 0; foreach (var s in _slots) if (s.IsEmpty) n++; return n; }

        public List<object> ToJson()
        {
            var l = new List<object>();
            foreach (var s in _slots) if (!s.IsEmpty) l.Add(new Dictionary<string, object> { { "id", s.ItemId }, { "count", (long)s.Count } });
            return l;
        }

        public void LoadJson(List<object> data)
        {
            for (int i = 0; i < _slots.Length; i++) _slots[i] = default;
            if (data != null)
                foreach (var o in data)
                    if (o is Dictionary<string, object> d) Add(Json.Str(d, "id"), (int)Json.Int(d, "count", 0, 0, 100000));
            Changed?.Invoke();
        }
    }
}
