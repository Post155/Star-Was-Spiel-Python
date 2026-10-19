using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>
    /// Zentrale Schadens- und Trefferverarbeitung. Die Arcade-Regeln des Originals bleiben unverändert
    /// (Rüstung: max(1, round(Schaden * (1 - Resistenz)))); zusätzlich verhindert das Ledger, dass dasselbe
    /// Projektil/Schadensereignis zweimal gewertet wird.
    /// </summary>
    public static class CombatSystem
    {
        public static int EffectiveDamage(int amount, double armorResistance)
            => Math.Max(1, PyMath.Round(amount * (1.0 - armorResistance)));
    }

    public sealed class HitLedger
    {
        private readonly HashSet<string> _seen = new HashSet<string>();
        private readonly Queue<string> _order = new Queue<string>();
        private readonly int _capacity;
        public HitLedger(int capacity = 512) { _capacity = capacity; }

        /// <summary>true = erstmals gesehen (Treffer zählt); false = Duplikat (ignorieren).</summary>
        public bool TryRegister(string eventId)
        {
            if (string.IsNullOrEmpty(eventId)) return true;
            if (!_seen.Add(eventId)) return false;
            _order.Enqueue(eventId);
            while (_order.Count > _capacity) _seen.Remove(_order.Dequeue());
            return true;
        }
    }
}
