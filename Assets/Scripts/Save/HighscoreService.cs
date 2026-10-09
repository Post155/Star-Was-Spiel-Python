namespace StarWarsUnity
{
    public static class HighscoreService
    {
        private const string Key = "starwars_highscore";
        public static int Load() => UnityEngine.PlayerPrefs.GetInt(Key, 0);
        public static void Save(int score)
        {
            int current = Load();
            if (score > current)
            {
                UnityEngine.PlayerPrefs.SetInt(Key, score);
                UnityEngine.PlayerPrefs.Save();
            }
        }
    }
}
