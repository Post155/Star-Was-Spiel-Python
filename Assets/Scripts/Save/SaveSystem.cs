using System.IO;
using UnityEngine;

namespace StarWarsUnity
{
    public static class SaveSystem
    {
        private static string Path => System.IO.Path.Combine(Application.persistentDataPath, "starwars_save.json");

        public static void Save(SaveGameData data)
        {
            if (data == null) return;
            File.WriteAllText(Path, JsonUtility.ToJson(data, true));
        }

        public static SaveGameData Load()
        {
            if (!File.Exists(Path)) return null;
            try { return JsonUtility.FromJson<SaveGameData>(File.ReadAllText(Path)); }
            catch { return null; }
        }

        public static void Delete(){ if(File.Exists(Path)) File.Delete(Path); }
    }
}
