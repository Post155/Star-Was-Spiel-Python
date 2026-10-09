using UnityEngine;

namespace StarWarsUnity
{
    public sealed class AssetLibrary : MonoBehaviour
    {
        public Sprite XWing => Load("Pixelarts/X_Wing");
        public Sprite MillenniumFalcon => Load("Pixelarts/millennium");
        public Sprite TieFighter => Load("Pixelarts/tie-fighter");
        public Sprite BattleDroid => Load("Pixelarts/Battle_Droid");
        public Sprite Torpedo => Load("Pixelarts/Torpedo");
        public Sprite Explosion => Load("Pixelarts/Explosion");
        public Sprite[] Asteroids => Resources.LoadAll<Sprite>("Pixelarts/Astroids");
        public Sprite RebelLogo => Load("Pixelarts/Star-Wars-Rebel-Logo");
        public Sprite EmpireLogo => Load("Pixelarts/Galactic-Empire-Logo");
        public Sprite Lightsabers => Load("Pixelarts/lichtschwerter");

        private static Sprite Load(string path) => Resources.Load<Sprite>(path);
    }
}
