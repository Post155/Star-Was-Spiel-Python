using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public static class RuntimeContent
    {
        public static Dictionary<ShipId, ShipDefinition> BuildShips(AssetLibrary assets)
        {
            var result = new Dictionary<ShipId, ShipDefinition>();
            Add(result, ShipId.XWing, "X-Wing", Faction.Rebels, assets.XWing, assets.Torpedo, GameConstants.ShipSpeedXWing, true);
            Add(result, ShipId.MillenniumFalcon, "Millennium Falcon", Faction.Rebels, assets.MillenniumFalcon, assets.Torpedo, GameConstants.ShipSpeedMillennium, false);
            Add(result, ShipId.TieFighter, "TIE Fighter", Faction.Empire, assets.TieFighter, assets.Torpedo, GameConstants.ShipSpeedTieFighter, true);
            Add(result, ShipId.BattleDroid, "Battle Droid", Faction.Empire, assets.BattleDroid, assets.Torpedo, GameConstants.ShipSpeedBattleDroid, false);
            return result;
        }

        private static void Add(Dictionary<ShipId, ShipDefinition> dict, ShipId id, string name, Faction faction, Sprite sprite,
            Sprite torpedo, float speed, bool canTorpedo)
        {
            var def = ScriptableObject.CreateInstance<ShipDefinition>();
            def.id = id; def.displayName = name; def.faction = faction; def.sprite = sprite; def.torpedoSprite = torpedo;
            def.moveSpeed = speed; def.scale = 96f / Mathf.Max(1f, sprite != null ? sprite.rect.height / sprite.pixelsPerUnit : 96f);
            def.canFireTorpedo = canTorpedo;
            ShipController.ApplyDefaultMuzzles(def);
            dict[id] = def;
        }

        public static List<EnemyArchetype> BuildEnemyArchetypes()
        {
            var list = new List<EnemyArchetype>();
            list.Add(Create("standard", "STANDARD", 4, 185, 520, 0, 1, new Vector2(1.10f,1.75f), new Vector2Int(1,2), .68f, new Vector2(.26f,.48f), .36f, 2, new Vector2(10,14), .14f, 100, new Vector2Int(0,45), 1f));
            list.Add(Create("fast", "SCHNELL", 3, 285, 760, 0, 1, new Vector2(.78f,1.30f), new Vector2Int(1,3), .61f, new Vector2(.16f,.31f), .58f, 2, new Vector2(9,13), .18f, 190, new Vector2Int(25,90), .88f));
            list.Add(Create("heavy", "SCHWER", 10, 125, 310, .28f, 2, new Vector2(1.20f,1.85f), new Vector2Int(2,3), .74f, new Vector2(.38f,.62f), .22f, 2, new Vector2(8,11.5f), .34f, 340, new Vector2Int(55,160), 1.18f));
            list.Add(Create("elite", "ELITE", 8, 250, 680, .14f, 2, new Vector2(.58f,.96f), new Vector2Int(2,4), .91f, new Vector2(.10f,.20f), .84f, 2, new Vector2(5.8f,8.4f), .58f, 650, new Vector2Int(110,320), 1.05f));
            return list;
        }

        private static EnemyArchetype Create(string key, string display, int hp, float speed, float acceleration, float armor,
            int laserDamage, Vector2 laserCooldown, Vector2Int burst, float accuracy, Vector2 reaction, float dodge, int torpedoDamage,
            Vector2 torpedoCooldown, float torpedoChance, int baseScore, Vector2Int bonus, float visualScale)
        {
            var a = ScriptableObject.CreateInstance<EnemyArchetype>();
            a.key = key; a.displayName = display; a.maxHp = hp; a.maxSpeed = speed; a.acceleration = acceleration; a.armorResistance = armor;
            a.laserDamage = laserDamage; a.laserCooldown = laserCooldown; a.burstRange = burst; a.accuracy = accuracy; a.reactionTime = reaction;
            a.dodgeChance = dodge; a.torpedoDamage = torpedoDamage; a.torpedoCooldown = torpedoCooldown; a.torpedoChance = torpedoChance;
            a.baseScore = baseScore; a.bonusScore = bonus; a.visualScaleMultiplier = visualScale;
            return a;
        }

        public static List<StarSystemDefinition> BuildSystems(AssetLibrary assets)
        {
            var list = new List<StarSystemDefinition>();
            AddSystem(list, "EARTH", new[] { "EARTH", "Milky-System" }, assets.LoadNamed("Pixelarts/Planets/milkyway/planet_earth"), new Color32(200,120,80,255), .5f, .5f, 1, new Color32(80,20,8,28));
            AddSystem(list, "SATURN", new[] { "SATURN", "Milky-System" }, assets.LoadNamed("Pixelarts/Planets/milkyway/planet_saturn"), new Color32(200,120,80,255), .6f, 1.3f, 2, new Color32(80,20,8,28));
            AddSystem(list, "BLACKHOLE", new[] { "BLACKHOLE", "ERROR" }, assets.LoadNamed("Pixelarts/Planets/milkyway/planet_schwarzesLoch"), new Color32(200,120,80,255), 2f, 2.5f, 5, new Color32(80,20,8,28));
            AddSystem(list, "TODESSTERN", new[] { "TODESSTERN", "Somewhere" }, assets.LoadNamed("Pixelarts/Planets/death_star/TodesternEins"), new Color32(200,120,80,255), 2f, 2f, 4, new Color32(80,20,8,28));
            AddSystem(list, "STERNZERSTÖRER", new[] { "STERNZERSTÖRER", "Somewhere" }, assets.LoadNamed("Pixelarts/Planets/death_star/Sternzerstörer"), new Color32(200,120,80,255), 2f, 2f, 4, new Color32(80,20,8,28));
            AddSystem(list, "TATOOINE", new[] { "TATOOINE", "Tatooine-System" }, assets.LoadNamed("Pixelarts/Planets/core_worlds/planet_tatooine"), new Color32(255,230,160,255), .9f, 1.25f, 2, new Color32(30,20,0,20));
            AddSystem(list, "PURPLE", new[] { "PURPLE", "Strange-Sektor" }, assets.LoadNamed("Pixelarts/Planets/core_worlds/planet_purple"), new Color32(180,200,220,255), .9f, 1.5f, 2, new Color32(16,24,60,12));
            AddSystem(list, "KAMINO", new[] { "KAMINO", "Kamino-System" }, assets.LoadNamed("Pixelarts/Planets/core_worlds/planet_kamino"), new Color32(160,200,230,255), 1.05f, 1.2f, 2, new Color32(12,24,36,10));
            AddSystem(list, "HOTH", new[] { "HOTH", "Hoth-System" }, assets.LoadNamed("Pixelarts/Planets/core_worlds/planet_hoth"), new Color32(200,220,255,255), 1.1f, 1.4f, 2, new Color32(8,16,40,28));
            var endor = AddSystem(list, "ENDOR", new[] { "ENDOR", "Endor-System" }, assets.LoadNamed("Pixelarts/Planets/core_worlds/planet_endor"), new Color32(180,230,180,255), 1.25f, 1.6f, 3, new Color32(10,30,12,24)); endor.moreEnemies = true;
            AddSystem(list, "CORUSCANT", new[] { "CORUSCANT", "Coruscant-System" }, assets.LoadNamed("Pixelarts/Planets/core_worlds/planet_corusant"), new Color32(220,210,200,255), .8f, 1.15f, 3, new Color32(40,30,30,18));
            AddSystem(list, "MUSTAFAR", new[] { "MUSTAFAR", "Mustafar-System" }, assets.LoadNamed("Pixelarts/Planets/core_worlds/planet_Mustafar"), new Color32(200,120,80,255), .9f, 1.6f, 3, new Color32(80,20,8,28));
            return list;
        }

        private static StarSystemDefinition AddSystem(List<StarSystemDefinition> list, string id, string[] lines, Sprite planet,
            Color tint, float density, float asteroidSpeed, int difficulty, Color filter)
        {
            var s = ScriptableObject.CreateInstance<StarSystemDefinition>();
            s.idName = id; s.displayLines = lines; s.starTint = tint; s.starDensity = density; s.asteroidSpeedMultiplier = asteroidSpeed;
            s.difficulty = difficulty; s.visualFilter = filter; s.planetSprites = planet != null ? new[] { planet } : new Sprite[0];
            list.Add(s); return s;
        }
    }

    public static class AssetLibraryExtensions
    {
        public static Sprite LoadNamed(this AssetLibrary _, string path) => Resources.Load<Sprite>(path);
    }
}
