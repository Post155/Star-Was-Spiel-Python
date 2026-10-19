using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>game/background/systems.py – Konfiguration eines Sternensystems.</summary>
    public sealed class StarSystem
    {
        public string IdName;
        public string[] DisplayLines;
        public string[] PlanetKeys = new string[0];
        public string[] ForegroundKeys = new string[0];
        public int[] StarTint;                 // RGB oder null
        public double StarDensity = 1.0;
        public double AsteroidSpeedMul = 1.0;
        public int Difficulty = 1;
        public int[] VisualFilter = { 0, 0, 0, 0 };   // RGBA
        public bool MoreEnemies;
    }

    /// <summary>Planetenbilder (normalisierter Schlüssel wie game/assets.py) und deren Resources-Pfade.</summary>
    public static class PlanetCatalog
    {
        public static readonly Dictionary<string, string> ResourcePaths = new Dictionary<string, string>
        {
            { "earth", "Pixelarts/Planets/milkyway/planet_earth" },
            { "saturn", "Pixelarts/Planets/milkyway/planet_saturn" },
            { "schwarzesloch", "Pixelarts/Planets/milkyway/planet_schwarzesLoch" },
            { "todesterneins", "Pixelarts/Planets/death_star/TodesternEins" },
            { "todesternzwei", "Pixelarts/Planets/death_star/TodesternZwei" },
            { "sternzerstoerer", "Pixelarts/Planets/death_star/Sternzerstoerer" },
            { "kamino", "Pixelarts/Planets/core_worlds/planet_kamino" },
            { "tatooine", "Pixelarts/Planets/core_worlds/planet_tatooine" },
            { "corusant", "Pixelarts/Planets/core_worlds/planet_corusant" },
            { "mustafar", "Pixelarts/Planets/core_worlds/planet_Mustafar" },
            { "hoth", "Pixelarts/Planets/core_worlds/planet_hoth" },
            { "purple", "Pixelarts/Planets/core_worlds/planet_purple" },
            { "endor", "Pixelarts/Planets/core_worlds/planet_endor" },
        };

        /// <summary>Systemschlüssel (z. B. "coruscant") -> Dateischlüssel ("corusant"), wie PLANET_NAME_ALIASES im Original.</summary>
        public static string ResolveKey(string key) => key == "coruscant" ? "corusant" : key;

        /// <summary>Alle 13 entdeckten Planeten – Fallback-Pool für Systeme ohne eigenes Planetenbild (assets['planet_images']).</summary>
        public static string[] AllKeys()
        {
            var l = new List<string>(ResourcePaths.Keys);
            return l.ToArray();
        }

        public static int[] Size(string key) => AssetMetrics.PlanetSizes[ResolveKey(key)];
    }

    /// <summary>game/background/system_manager.py – Reihenfolge der Systeme (EARTH fix zuerst, Rest zufällig).</summary>
    public sealed class SystemManager
    {
        public readonly List<StarSystem> Systems;
        public List<StarSystem> Order = new List<StarSystem>();
        public int OrderIndex;
        public int LevelIndex;
        public readonly HashSet<string> Visited = new HashSet<string>();

        public SystemManager(ISimRandom rng)
        {
            Systems = Build();
            var first = Systems[0];
            var others = Systems.GetRange(1, Systems.Count - 1);
            rng.Shuffle(others);
            Order.Add(first); Order.AddRange(others);
        }

        public StarSystem Current => Order.Count == 0 ? null : Order[OrderIndex];
        public string CurrentId => Current != null ? Current.IdName : "";
        public int NextIndex => Order.Count == 0 ? 0 : (OrderIndex + 1) % Order.Count;
        public StarSystem Target => Order.Count == 0 ? null : Order[NextIndex];
        public void AdvanceToIndex(int idx) { if (Order.Count == 0) return; OrderIndex = ((idx % Order.Count) + Order.Count) % Order.Count; LevelIndex = 0; }
        public void MarkVisitedCurrent() { if (Current != null) Visited.Add(Current.IdName); }

        /// <summary>Wendet die vom Host bestimmte (zufällige) Reihenfolge auf einem Client an.</summary>
        public void SetOrderByIds(IList<string> ids)
        {
            if (ids == null || ids.Count == 0) return;
            var byId = new Dictionary<string, StarSystem>();
            foreach (var s in Systems) byId[s.IdName] = s;
            var ordered = new List<StarSystem>();
            foreach (var id in ids) if (byId.TryGetValue(id, out var s)) ordered.Add(s);
            if (ordered.Count == 0) return;
            foreach (var s in Systems) if (!ids.Contains(s.IdName)) ordered.Add(s);
            Order = ordered;
            OrderIndex = Math.Min(OrderIndex, Math.Max(0, Order.Count - 1));
            LevelIndex = 0;
        }

        /// <summary>Exakt die 12 Systeme aus build_systems(); BLACKHOLE/TODESSTERN/STERNZERSTÖRER haben im Original keinen Planetenschlüssel (Asset-Namen passen nicht).</summary>
        public static List<StarSystem> Build()
        {
            var warm = new[] { 200, 120, 80 };
            var warmFilter = new[] { 80, 20, 8, 28 };
            return new List<StarSystem>
            {
                new StarSystem { IdName = "EARTH", DisplayLines = new[] { "EARTH", "Milky-System" }, PlanetKeys = new[] { "earth" }, StarTint = warm, StarDensity = 0.5, AsteroidSpeedMul = 0.5, Difficulty = 1, VisualFilter = warmFilter },
                new StarSystem { IdName = "SATURN", DisplayLines = new[] { "SATURN", "Milky-System" }, PlanetKeys = new[] { "saturn" }, StarTint = warm, StarDensity = 0.6, AsteroidSpeedMul = 1.3, Difficulty = 2, VisualFilter = warmFilter },
                new StarSystem { IdName = "BLACKHOLE", DisplayLines = new[] { "BLACKHOLE", "ERROR" }, StarTint = warm, StarDensity = 2.0, AsteroidSpeedMul = 2.5, Difficulty = 5, VisualFilter = warmFilter },
                new StarSystem { IdName = "TODESSTERN", DisplayLines = new[] { "TODESSTERN", "Somewhere" }, StarTint = warm, StarDensity = 2.0, AsteroidSpeedMul = 2.0, Difficulty = 4, VisualFilter = warmFilter },
                new StarSystem { IdName = "STERNZERSTÖRER", DisplayLines = new[] { "STERNZERSTÖRER", "Somewhere" }, StarTint = warm, StarDensity = 2.0, AsteroidSpeedMul = 2.0, Difficulty = 4, VisualFilter = warmFilter },
                new StarSystem { IdName = "TATOOINE", DisplayLines = new[] { "TATOOINE", "Tatooine-System" }, PlanetKeys = new[] { "tatooine" }, StarTint = new[] { 255, 230, 160 }, StarDensity = 0.9, AsteroidSpeedMul = 1.25, Difficulty = 2, VisualFilter = new[] { 30, 20, 0, 20 } },
                new StarSystem { IdName = "PURPLE", DisplayLines = new[] { "PURPLE", "Strange-Sektor" }, PlanetKeys = new[] { "purple" }, StarTint = new[] { 180, 200, 220 }, StarDensity = 0.9, AsteroidSpeedMul = 1.5, Difficulty = 2, VisualFilter = new[] { 16, 24, 60, 12 } },
                new StarSystem { IdName = "KAMINO", DisplayLines = new[] { "KAMINO", "Kamino-System" }, PlanetKeys = new[] { "kamino" }, StarTint = new[] { 160, 200, 230 }, StarDensity = 1.05, AsteroidSpeedMul = 1.2, Difficulty = 2, VisualFilter = new[] { 12, 24, 36, 10 } },
                new StarSystem { IdName = "HOTH", DisplayLines = new[] { "HOTH", "Hoth-System" }, PlanetKeys = new[] { "hoth" }, StarTint = new[] { 200, 220, 255 }, StarDensity = 1.1, AsteroidSpeedMul = 1.4, Difficulty = 2, VisualFilter = new[] { 8, 16, 40, 28 } },
                new StarSystem { IdName = "ENDOR", DisplayLines = new[] { "ENDOR", "Endor-System" }, PlanetKeys = new[] { "endor" }, StarTint = new[] { 180, 230, 180 }, StarDensity = 1.25, AsteroidSpeedMul = 1.6, MoreEnemies = true, Difficulty = 3, VisualFilter = new[] { 10, 30, 12, 24 } },
                new StarSystem { IdName = "CORUSCANT", DisplayLines = new[] { "CORUSCANT", "Coruscant-System" }, PlanetKeys = new[] { "coruscant" }, StarTint = new[] { 220, 210, 200 }, StarDensity = 0.8, AsteroidSpeedMul = 1.15, Difficulty = 3, VisualFilter = new[] { 40, 30, 30, 18 } },
                new StarSystem { IdName = "MUSTAFAR", DisplayLines = new[] { "MUSTAFAR", "Mustafar-System" }, PlanetKeys = new[] { "mustafar" }, StarTint = warm, StarDensity = 0.9, AsteroidSpeedMul = 1.6, Difficulty = 3, VisualFilter = warmFilter },
            };
        }
    }
}
