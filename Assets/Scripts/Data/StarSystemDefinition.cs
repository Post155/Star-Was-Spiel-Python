using UnityEngine;

namespace StarWarsUnity
{
    [CreateAssetMenu(menuName = "Star Wars/Star System")]
    public sealed class StarSystemDefinition : ScriptableObject
    {
        public string idName;
        public string[] displayLines;
        public Sprite[] planetSprites;
        public Sprite[] foregroundSprites;
        public Color starTint = Color.white;
        [Min(0.1f)] public float starDensity = 1f;
        [Min(0.1f)] public float asteroidSpeedMultiplier = 1f;
        public int difficulty = 1;
        public Color visualFilter = new Color(0f, 0f, 0f, 0f);
        public bool moreEnemies;
    }
}
