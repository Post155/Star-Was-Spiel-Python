using System.Collections.Generic;
using UnityEngine;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>
    /// Lädt die Original-Pixelarts aus Resources/Pixelarts. Sprites werden aus der Texture2D erzeugt (Pixels-per-Unit = 1,
    /// Filter = Point), damit sie unabhängig von den Import-Einstellungen scharf und pixelgenau (1 Pixel = 1 Einheit) erscheinen.
    /// </summary>
    public static class SpriteLibrary
    {
        private static readonly Dictionary<string, Sprite> Cache = new Dictionary<string, Sprite>();
        private static Sprite _white, _circle;
        public static readonly List<string> MissingAssets = new List<string>();

        public static Sprite Load(string resourcePath)
        {
            if (Cache.TryGetValue(resourcePath, out var cached)) return cached;
            var tex = Resources.Load<Texture2D>(resourcePath);
            Sprite sprite = null;
            if (tex != null)
            {
                tex.filterMode = FilterMode.Point;
                tex.wrapMode = TextureWrapMode.Clamp;
                sprite = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f), 1f);
            }
            else
            {
                // Dokumentierte Ersatzlösung: sichtbares magentafarbenes Quadrat statt eines leeren Objekts.
                if (!MissingAssets.Contains(resourcePath)) { MissingAssets.Add(resourcePath); Debug.LogWarning("Pixelart fehlt: " + resourcePath); }
                sprite = Placeholder();
            }
            Cache[resourcePath] = sprite;
            return sprite;
        }

        private static Sprite Placeholder()
        {
            var t = new Texture2D(8, 8, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
            var px = new Color32[64]; for (int i = 0; i < 64; i++) px[i] = new Color32(255, 0, 255, 255);
            t.SetPixels32(px); t.Apply();
            return Sprite.Create(t, new Rect(0, 0, 8, 8), new Vector2(0.5f, 0.5f), 1f);
        }

        public static Sprite White
        {
            get
            {
                if (_white != null) return _white;
                var t = new Texture2D(2, 2, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
                var px = new Color32[4]; for (int i = 0; i < 4; i++) px[i] = new Color32(255, 255, 255, 255);
                t.SetPixels32(px); t.Apply();
                return _white = Sprite.Create(t, new Rect(0, 0, 2, 2), new Vector2(0.5f, 0.5f), 2f);   // 2 px bei PPU 2 => 1x1 Einheit
            }
        }

        public static Sprite Circle
        {
            get
            {
                if (_circle != null) return _circle;
                const int n = 64;
                var t = new Texture2D(n, n, TextureFormat.RGBA32, false) { filterMode = FilterMode.Bilinear };
                var px = new Color32[n * n];
                for (int y = 0; y < n; y++) for (int x = 0; x < n; x++)
                {
                    float dx = x - (n - 1) / 2f, dy = y - (n - 1) / 2f; float d = Mathf.Sqrt(dx * dx + dy * dy);
                    byte a = (byte)(Mathf.Clamp01((n / 2f - d)) * 255);
                    px[y * n + x] = new Color32(255, 255, 255, a);
                }
                t.SetPixels32(px); t.Apply();
                return _circle = Sprite.Create(t, new Rect(0, 0, n, n), new Vector2(0.5f, 0.5f), n);   // Durchmesser 1 Einheit
            }
        }

        public static Sprite Ship(string key) => Load(ShipCatalog.Get(key).SpriteResource);
        public static Sprite Torpedo => Load("Pixelarts/Torpedo");
        public static Sprite Explosion => Load("Pixelarts/Explosion");
        public static Sprite RebelLogo => Load("Pixelarts/Star-Wars-Rebel-Logo");
        public static Sprite EmpireLogo => Load("Pixelarts/Galactic-Empire-Logo");

        private static Sprite[] _asteroids;
        public static Sprite AsteroidFrame(int index)
        {
            if (_asteroids == null)
            {
                _asteroids = new Sprite[AssetMetrics.AsteroidFrameCount];
                for (int i = 0; i < _asteroids.Length; i++) _asteroids[i] = Load("Pixelarts/Astroids/frame_" + i.ToString("00"));
            }
            return _asteroids[((index % _asteroids.Length) + _asteroids.Length) % _asteroids.Length];
        }

        /// <summary>Lichtschwert-Lebensanzeige: oberes Blatthälfte (blau, Rebellen) bzw. untere (rot, Imperium) des 1536x1024-Sheets.</summary>
        public static Sprite Lightsaber(bool rebels)
        {
            string key = rebels ? "lightsaber_blue" : "lightsaber_red";
            if (Cache.TryGetValue(key, out var c)) return c;
            var tex = Resources.Load<Texture2D>("Pixelarts/lichtschwerter");
            Sprite s;
            if (tex == null) s = Placeholder();
            else
            {
                tex.filterMode = FilterMode.Bilinear;
                int half = tex.height / 2;
                // Unity-Texturkoordinaten beginnen unten: Python-Zeile 0..511 (oben, blau) = Unity y 512..1023.
                s = Sprite.Create(tex, new Rect(0, rebels ? half : 0, tex.width, half), new Vector2(0.5f, 0.5f), 1f);
            }
            Cache[key] = s; return s;
        }

        public static Sprite Planet(string key)
        {
            string resolved = PlanetCatalog.ResolveKey(key);
            return PlanetCatalog.ResourcePaths.TryGetValue(resolved, out var path) ? Load(path) : Placeholder();
        }
    }
}
