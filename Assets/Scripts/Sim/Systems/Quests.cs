using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    public enum QuestObjective { DestroyAsteroids, DestroyEnemies, ReachScore, EnterSystems }
    public enum QuestState { Available, Active, Completed, Claimed }

    public sealed class QuestDefinition
    {
        public string Id, Title, Description;
        public QuestObjective Objective;
        public int Target;
        public string RewardItemId; public int RewardCount;
    }

    public sealed class QuestProgress { public QuestState State = QuestState.Available; public int Progress; }

    /// <summary>
    /// Questsystem (neu): Annahme, Fortschritt über Spielereignisse, Abschluss, Belohnung (nur einmal abholbar), Speicherung.
    /// </summary>
    public sealed class QuestLog
    {
        private readonly Dictionary<string, QuestDefinition> _defs = new Dictionary<string, QuestDefinition>();
        private readonly Dictionary<string, QuestProgress> _state = new Dictionary<string, QuestProgress>();
        public event Action<QuestDefinition> Completed;
        public event Action Changed;

        public static QuestLog CreateDefault()
        {
            var q = new QuestLog();
            q.Register(new QuestDefinition { Id = "q_asteroids_10", Title = "Asteroidenfeld räumen", Description = "Zerstöre 10 Asteroiden.", Objective = QuestObjective.DestroyAsteroids, Target = 10, RewardItemId = "repair_kit", RewardCount = 1 });
            q.Register(new QuestDefinition { Id = "q_enemies_5", Title = "Feindkontakt", Description = "Zerstöre 5 feindliche Schiffe.", Objective = QuestObjective.DestroyEnemies, Target = 5, RewardItemId = "torpedo_crate", RewardCount = 2 });
            q.Register(new QuestDefinition { Id = "q_score_3000", Title = "Ass der Galaxis", Description = "Erreiche 3000 Punkte in einer Runde.", Objective = QuestObjective.ReachScore, Target = 3000, RewardItemId = "shield_booster", RewardCount = 1 });
            q.Register(new QuestDefinition { Id = "q_systems_3", Title = "Hyperraum-Reisender", Description = "Fliege insgesamt in 3 neue Sternensysteme (Systemwechsel im Spiel).", Objective = QuestObjective.EnterSystems, Target = 3, RewardItemId = "kyber_crystal", RewardCount = 1 });
            return q;
        }

        public void Register(QuestDefinition d) { _defs[d.Id] = d; if (!_state.ContainsKey(d.Id)) _state[d.Id] = new QuestProgress(); }
        public IEnumerable<QuestDefinition> Definitions => _defs.Values;
        public QuestProgress GetProgress(string id) => _state.TryGetValue(id ?? "", out var p) ? p : null;

        public bool Accept(string id)
        {
            if (!_state.TryGetValue(id ?? "", out var p) || p.State != QuestState.Available) return false;
            p.State = QuestState.Active; p.Progress = 0; Changed?.Invoke(); return true;
        }

        /// <summary>Meldet ein Spielereignis. Zählende Ziele addieren, ReachScore übernimmt den Maximalwert.</summary>
        public void Report(QuestObjective kind, int amount)
        {
            foreach (var d in _defs.Values)
            {
                if (d.Objective != kind) continue;
                var p = _state[d.Id];
                if (p.State != QuestState.Active) continue;
                p.Progress = kind == QuestObjective.ReachScore ? Math.Max(p.Progress, amount) : p.Progress + amount;
                if (p.Progress >= d.Target) { p.Progress = d.Target; p.State = QuestState.Completed; Completed?.Invoke(d); }
                Changed?.Invoke();
            }
        }

        /// <summary>Gibt die Belohnung genau einmal aus. false = nicht abgeschlossen, bereits abgeholt oder Inventar voll (Quest bleibt dann abholbar).</summary>
        public bool Claim(string id, Inventory inventory)
        {
            if (!_state.TryGetValue(id ?? "", out var p) || p.State != QuestState.Completed) return false;
            var d = _defs[id];
            if (!string.IsNullOrEmpty(d.RewardItemId) && d.RewardCount > 0)
            {
                if (inventory == null) return false;
                if (inventory.Add(d.RewardItemId, d.RewardCount) > 0) return false;
            }
            p.State = QuestState.Claimed; Changed?.Invoke(); return true;
        }

        public Dictionary<string, object> ToJson()
        {
            var d = new Dictionary<string, object>();
            foreach (var kv in _state) d[kv.Key] = new Dictionary<string, object> { { "state", kv.Value.State.ToString() }, { "progress", (long)kv.Value.Progress } };
            return d;
        }

        public void LoadJson(Dictionary<string, object> data)
        {
            if (data == null) return;
            foreach (var kv in data)
            {
                if (!_state.ContainsKey(kv.Key) || !(kv.Value is Dictionary<string, object> d)) continue;
                if (Enum.TryParse(Json.Str(d, "state"), out QuestState st)) _state[kv.Key].State = st;
                _state[kv.Key].Progress = (int)Json.Int(d, "progress", 0, 0, int.MaxValue);
            }
            Changed?.Invoke();
        }
    }
}
