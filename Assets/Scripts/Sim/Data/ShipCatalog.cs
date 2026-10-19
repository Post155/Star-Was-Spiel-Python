using System.Collections.Generic;

namespace StarWars.Sim
{
    public enum Faction { Rebels, Empire }

    /// <summary>Statische Schiffsdaten (entspricht game/entities/ships.py + constants.py).</summary>
    public sealed class ShipInfo
    {
        public string Key;            // "xwing", "milleniumfalcon" (Schreibweise wie im Original), "tiefighter", "battledroid"
        public string ClassName;      // Pygame-Klassenname (Schlüssel für Gegner-Metriken)
        public string DisplayName;
        public Faction Faction;
        public int Speed;
        public bool HasTorpedo;
        public bool TorpedoFromHitbox;   // XWing: Torpedo(hitbox.centerx, y); TIE: Torpedo(x+w*0.47, y+h*0.12)
        public double[] LaserFx, LaserFy;
        public string SpriteResource;    // Resources-Pfad
        public string OpposingKey;       // Gegnerschiff laut OPPOSING_SHIP_BY_PLAYER
    }

    public static class ShipCatalog
    {
        public static readonly ShipInfo XWing = new ShipInfo
        {
            Key = "xwing", ClassName = "XWing", DisplayName = "X-Wing", Faction = Faction.Rebels, Speed = GameConstants.ShipSpeedXWing,
            HasTorpedo = true, TorpedoFromHitbox = true, LaserFx = new[] { 0.18, 0.82 }, LaserFy = new[] { 0.3, 0.3 },
            SpriteResource = "Pixelarts/X_Wing", OpposingKey = "tiefighter"
        };
        public static readonly ShipInfo Falcon = new ShipInfo
        {
            Key = "milleniumfalcon", ClassName = "MillenniumFalcon", DisplayName = "Millennium Falcon", Faction = Faction.Rebels, Speed = GameConstants.ShipSpeedMillennium,
            HasTorpedo = false, LaserFx = new[] { 0.43, 0.58 }, LaserFy = new[] { 0.06, 0.06 },
            SpriteResource = "Pixelarts/millennium", OpposingKey = "battledroid"
        };
        public static readonly ShipInfo Tie = new ShipInfo
        {
            Key = "tiefighter", ClassName = "Tiefighter", DisplayName = "TIE Fighter", Faction = Faction.Empire, Speed = GameConstants.ShipSpeedTieFighter,
            HasTorpedo = true, TorpedoFromHitbox = false, LaserFx = new[] { 0.44, 0.55 }, LaserFy = new[] { 0.30, 0.30 },
            SpriteResource = "Pixelarts/tie-fighter", OpposingKey = "xwing"
        };
        public static readonly ShipInfo Droid = new ShipInfo
        {
            Key = "battledroid", ClassName = "BattleDroid", DisplayName = "Battle Droid", Faction = Faction.Empire, Speed = GameConstants.ShipSpeedBattleDroid,
            HasTorpedo = false, LaserFx = new[] { 0.05, 0.94 }, LaserFy = new[] { 0.01, 0.01 },
            SpriteResource = "Pixelarts/Battle_Droid", OpposingKey = "milleniumfalcon"
        };

        public static readonly ShipInfo[] All = { XWing, Falcon, Tie, Droid };

        public static ShipInfo Get(string key)
        {
            foreach (var s in All) if (s.Key == key) return s;
            return XWing;   // wie images.get(ship_name, images["xwing"]) im Original
        }

        public static bool IsValid(string key) { foreach (var s in All) if (s.Key == key) return true; return false; }

        public static ShipInfo[] ForFaction(Faction f)
        {
            var l = new List<ShipInfo>();
            foreach (var s in All) if (s.Faction == f) l.Add(s);
            return l.ToArray();
        }

        public static string FactionKey(Faction f) => f == Faction.Rebels ? "rebels" : "empire";
    }

    /// <summary>Simulationsuhr in Millisekunden (ersetzt pygame.time.get_ticks()); wird pro Tick um 1000/60 erhöht.</summary>
    public sealed class SimClock
    {
        public double NowMs;
        public void Advance(double ms) { NowMs += ms; }
    }
}
