using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    public sealed class PointsPlayerConfig
    {
        public string Name, Ship, Faction, Difficulty;
    }

    public sealed class PointsResultRow
    {
        public string Name; public int Score; public string System; public bool Dead;
    }

    /// <summary>
    /// Lokaler Punktekampf (game/points_fight.py): zwei VOLLSTÄNDIG getrennte Einzelspielerwelten.
    /// Die Welten teilen weder Gegner, Geschosse, Asteroiden noch Treffer; nur die Anzeige ist gemeinsam.
    /// Ein Ghost ist ausschließlich eine Anzeigeinformation (keine Hitbox, kein Spielobjekt).
    /// </summary>
    public sealed class PointsFightMatch
    {
        public const int WorldWidth = 400, WorldHeight = 600;   // halbe Fensterbreite wie im Original bei 800x600
        public readonly PointsPlayerConfig[] Configs;
        public readonly SinglePlayerWorld[] Worlds = new SinglePlayerWorld[2];
        public long Ticks { get; private set; }
        public bool Over { get; private set; }
        public int DurationMs = GameConstants.PvpScoreLimitMs;
        public List<PointsResultRow> Result { get; private set; }

        public PointsFightMatch(PointsPlayerConfig a, PointsPlayerConfig b, Func<ISimRandom> rngFactory = null)
        {
            if (a == null || b == null) throw new ArgumentException("Lokaler Punktekampf benötigt genau zwei Spieler.");
            Configs = new[] { a, b };
            for (int i = 0; i < 2; i++)
                Worlds[i] = new SinglePlayerWorld(WorldWidth, WorldHeight, Configs[i].Ship, Configs[i].Difficulty, rngFactory != null ? rngFactory() : new SimRandom());
        }

        public int ElapsedMs => (int)(Ticks * GameConstants.TickMs);
        public int RemainingMs => Math.Max(0, DurationMs - ElapsedMs);

        public void Step(PlayerInput p1, PlayerInput p2)
        {
            if (Over) return;
            Ticks++;
            Worlds[0].Step(p1);
            Worlds[1].Step(p2);
            if (ElapsedMs >= DurationMs || (Worlds[0].Dead && Worlds[1].Dead))
            {
                Over = true;
                Result = new List<PointsResultRow>();
                for (int i = 0; i < 2; i++)
                    Result.Add(new PointsResultRow { Name = Configs[i].Name, Score = Worlds[i].Score, System = Worlds[i].Background.CurrentSystemName, Dead = Worlds[i].Dead });
                Result.Sort((x, y) => y.Score.CompareTo(x.Score));
            }
        }

        /// <summary>Sieger-Name oder null bei Gleichstand.</summary>
        public string WinnerName()
        {
            if (Result == null || Result.Count < 2) return null;
            return Result[0].Score == Result[1].Score ? null : Result[0].Name;
        }
    }
}
