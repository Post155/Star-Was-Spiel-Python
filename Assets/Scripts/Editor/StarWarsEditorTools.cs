using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using StarWars.Game;
using StarWars.Sim;

namespace StarWars.EditorTools
{
    /// <summary>
    /// Editor-Automatisierung (Menü "Star Wars"): Pixelart-Import reparieren, Szenen + Build Settings + Pool-Prefabs erzeugen,
    /// ScriptableObject-Daten exportieren. Die mitgelieferten Szenen/Prefabs sind bereits vorhanden; diese Werkzeuge stellen
    /// sie bei Bedarf wiederholbar her (z. B. falls Unity eine Datei beim ersten Import beanstandet).
    /// </summary>
    public static class StarWarsEditorTools
    {
        private const string ScenesDir = "Assets/Scenes";
        private const string PrefabDir = "Assets/Resources/Prefabs";
        private const string ContentDir = "Assets/Resources/Content";

        [MenuItem("Star Wars/1) Alles einrichten (Import, Szenen, Prefabs, Daten)")]
        public static void SetupAll()
        {
            FixPixelArtImport();
            CreatePoolPrefabs();
            CreateScenes();
            ExportContentAssets();
            Debug.Log("Star Wars: Einrichtung abgeschlossen. Start mit der Szene 'MainMenu'.");
        }

        [InitializeOnLoadMethod]
        private static void AutoSetupOnce()
        {
            EditorApplication.delayCall += () =>
            {
                try
                {
                    if (EditorBuildSettings.scenes == null || EditorBuildSettings.scenes.Length == 0) RegisterBuildScenes();
                }
                catch (System.Exception ex) { Debug.LogWarning("Star Wars Auto-Setup: " + ex.Message); }
            };
        }

        // ------------------------------------------------------------------ Pixelart-Import
        [MenuItem("Star Wars/Pixelart-Import reparieren (Point, PPU 1, unkomprimiert)")]
        public static void FixPixelArtImport()
        {
            int fixedCount = 0;
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets/Resources/Pixelarts" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null) continue;
                bool changed = importer.textureType != TextureImporterType.Sprite || importer.filterMode != FilterMode.Point || importer.mipmapEnabled
                    || importer.spritePixelsPerUnit != 1f || importer.textureCompression != TextureImporterCompression.Uncompressed;
                if (!changed) continue;
                importer.textureType = TextureImporterType.Sprite;
                importer.spriteImportMode = SpriteImportMode.Single;
                importer.spritePixelsPerUnit = 1f;
                importer.filterMode = FilterMode.Point;
                importer.mipmapEnabled = false;
                importer.alphaIsTransparency = true;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.maxTextureSize = 4096;
                importer.SaveAndReimport();
                fixedCount++;
            }
            Debug.Log("Star Wars: Pixelart-Import geprüft, korrigiert: " + fixedCount);
        }

        // ------------------------------------------------------------------ Prefabs
        [MenuItem("Star Wars/Pool-Prefabs neu erzeugen")]
        public static void CreatePoolPrefabs()
        {
            EnsureFolder("Assets/Resources", "Prefabs");
            foreach (var name in PoolNames)
            {
                var go = new GameObject("Pool_" + name);
                go.AddComponent<SpriteRenderer>();
                PrefabUtility.SaveAsPrefabAsset(go, PrefabDir + "/Pool_" + name + ".prefab");
                Object.DestroyImmediate(go);
            }
            AssetDatabase.SaveAssets();
        }

        public static readonly string[] PoolNames =
        {
            "planets", "stars1", "stars2", "filter", "foreground", "asteroids", "lasers", "torpedoes", "enemies", "hpbg", "hpfill",
            "etorp", "elaser", "player", "players", "explosions", "fx", "ghost", "dbg"
        };

        // ------------------------------------------------------------------ Szenen
        [MenuItem("Star Wars/Szenen neu erzeugen und in Build Settings eintragen")]
        public static void CreateScenes()
        {
            EnsureFolder("Assets", "Scenes");
            foreach (var name in SceneNames.All)
            {
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var cam = new GameObject("Main Camera"); cam.tag = "MainCamera"; var c = cam.AddComponent<Camera>();
                c.orthographic = true; c.clearFlags = CameraClearFlags.SolidColor; c.backgroundColor = Color.black;
                new GameObject("SceneBootstrap").AddComponent<SceneBootstrap>();
                EditorSceneManager.SaveScene(scene, ScenesDir + "/" + name + ".unity");
            }
            RegisterBuildScenes();
        }

        [MenuItem("Star Wars/Build Settings: Szenen eintragen")]
        public static void RegisterBuildScenes()
        {
            var list = new List<EditorBuildSettingsScene>();
            foreach (var name in SceneNames.All)
            {
                string path = ScenesDir + "/" + name + ".unity";
                if (File.Exists(path)) list.Add(new EditorBuildSettingsScene(path, true));
            }
            EditorBuildSettings.scenes = list.ToArray();
        }

        // ------------------------------------------------------------------ ScriptableObjects
        [MenuItem("Star Wars/ScriptableObject-Daten exportieren")]
        public static void ExportContentAssets()
        {
            EnsureFolder("Assets/Resources", "Content");
            EnsureFolder(ContentDir, "Items"); EnsureFolder(ContentDir, "Ships"); EnsureFolder(ContentDir, "Enemies"); EnsureFolder(ContentDir, "Systems");

            foreach (var item in ItemDatabase.CreateDefault().All)
            {
                string path = ContentDir + "/Items/" + item.Id + ".asset";
                if (AssetDatabase.LoadAssetAtPath<ItemDefinitionAsset>(path) != null) continue;
                var a = ScriptableObject.CreateInstance<ItemDefinitionAsset>();
                a.id = item.Id; a.displayName = item.Name; a.description = item.Description; a.type = item.Type; a.value = item.Value; a.maxStack = item.MaxStack;
                AssetDatabase.CreateAsset(a, path);
            }
            foreach (var ship in ShipCatalog.All)
            {
                string path = ContentDir + "/Ships/" + ship.Key + ".asset";
                if (AssetDatabase.LoadAssetAtPath<ShipDefinitionAsset>(path) != null) continue;
                var m = AssetMetrics.Ships[ship.Key];
                var a = ScriptableObject.CreateInstance<ShipDefinitionAsset>();
                a.key = ship.Key; a.displayName = ship.DisplayName; a.faction = ship.Faction; a.speed = ship.Speed; a.hasTorpedo = ship.HasTorpedo;
                a.pixelWidth = m.Width; a.pixelHeight = m.Height; a.hitboxWidth = m.HitW; a.hitboxHeight = m.HitH;
                a.sprite = Resources.Load<Sprite>(ship.SpriteResource);
                AssetDatabase.CreateAsset(a, path);
            }
            foreach (var kv in EnemyArchetypes.All)
            {
                string path = ContentDir + "/Enemies/" + kv.Key + ".asset";
                if (AssetDatabase.LoadAssetAtPath<EnemyArchetypeAsset>(path) != null) continue;
                var e = kv.Value; var a = ScriptableObject.CreateInstance<EnemyArchetypeAsset>();
                a.key = e.Key; a.displayName = e.DisplayName; a.maxHp = e.MaxHp; a.maxSpeed = (float)e.MaxSpeed; a.acceleration = (float)e.Acceleration; a.armorResistance = (float)e.ArmorResistance;
                a.accuracy = (float)e.Accuracy; a.dodgeChance = (float)e.DodgeChance; a.torpedoChance = (float)e.TorpedoChance; a.baseScore = e.BaseScore;
                AssetDatabase.CreateAsset(a, path);
            }
            foreach (var s in SystemManager.Build())
            {
                string path = ContentDir + "/Systems/" + s.IdName.Replace("Ö", "OE") + ".asset";
                if (AssetDatabase.LoadAssetAtPath<StarSystemAsset>(path) != null) continue;
                var a = ScriptableObject.CreateInstance<StarSystemAsset>();
                a.idName = s.IdName; a.displayLines = s.DisplayLines; a.planetKeys = s.PlanetKeys; a.starDensity = (float)s.StarDensity; a.asteroidSpeedMultiplier = (float)s.AsteroidSpeedMul; a.difficulty = s.Difficulty;
                AssetDatabase.CreateAsset(a, path);
            }
            AssetDatabase.SaveAssets(); AssetDatabase.Refresh();
        }

        private static void EnsureFolder(string parent, string child)
        {
            if (!AssetDatabase.IsValidFolder(parent + "/" + child)) AssetDatabase.CreateFolder(parent, child);
        }
    }
}
