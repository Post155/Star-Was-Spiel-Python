using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>Wiederverwendbarer Pool von SpriteRendern (vermeidet Instantiate/Destroy pro Frame).</summary>
    public sealed class SpritePool
    {
        private readonly Transform _parent;
        private readonly List<SpriteRenderer> _items = new List<SpriteRenderer>();
        private int _used;
        private readonly string _name;
        private GameObject _prefab; private bool _prefabTried;
        public SpritePool(Transform parent, string name) { _parent = parent; _name = name; }

        public void Begin() { _used = 0; }

        public SpriteRenderer Draw(Sprite sprite, Vector3 localPos, float width, float height, int order, Color color, bool flipX = false, bool flipY = false, float rotZ = 0f)
        {
            SpriteRenderer sr;
            if (_used < _items.Count) sr = _items[_used];
            else
            {
                if (!_prefabTried) { _prefab = Resources.Load<GameObject>("Prefabs/Pool_" + _name); _prefabTried = true; }
                GameObject go;
                if (_prefab != null) go = Object.Instantiate(_prefab);   // Prefab aus dem Projekt (Material/Sorting-Layer frei anpassbar)
                else go = new GameObject();
                go.name = _name + "_" + _items.Count;
                go.transform.SetParent(_parent, false);
                sr = go.GetComponent<SpriteRenderer>();
                if (sr == null) sr = go.AddComponent<SpriteRenderer>();
                _items.Add(sr);
            }
            _used++;
            if (!sr.gameObject.activeSelf) sr.gameObject.SetActive(true);
            sr.sprite = sprite; sr.color = color; sr.sortingOrder = order;
            var size = sprite.rect.size;
            float sx = width / Mathf.Max(1f, size.x), sy = height / Mathf.Max(1f, size.y);
            sr.transform.localPosition = localPos;
            sr.transform.localRotation = Quaternion.Euler(0f, 0f, rotZ);
            sr.transform.localScale = new Vector3(flipX ? -sx : sx, flipY ? -sy : sy, 1f);
            return sr;
        }

        public void End() { for (int i = _used; i < _items.Count; i++) if (_items[i].gameObject.activeSelf) _items[i].gameObject.SetActive(false); }
    }

    /// <summary>
    /// Eine Spielfläche (Welt-Container + Kamera mit Viewport + HUD-Canvas). Koordinaten sind Pygame-Pixel (Ursprung oben links);
    /// <see cref="P"/> übersetzt in Unity-Weltkoordinaten (y nach oben). Der Punktekampf nutzt zwei Stages mit eigenen Kameras.
    /// </summary>
    public sealed class Stage
    {
        public readonly int Width, Height;
        public readonly GameObject Root;
        public readonly Camera Camera;
        public readonly Canvas Canvas;
        public readonly RectTransform CanvasRect;
        /// <summary>Optional: liefert das aktuelle Viewport-Rechteck (wird pro Frame ausgewertet, damit Fenstergrößen-Änderungen greifen).</summary>
        public System.Func<Rect> ViewportFn;
        private readonly Dictionary<string, SpritePool> _pools = new Dictionary<string, SpritePool>();
        private readonly Vector3 _offset;

        public Stage(string name, Vector3 worldOffset, int width, int height, Rect viewport, int cameraDepth)
        {
            Width = width; Height = height; _offset = worldOffset;
            Root = new GameObject(name + "_World");
            Root.transform.position = worldOffset;
            var camGo = new GameObject(name + "_Camera");
            camGo.transform.position = worldOffset + new Vector3(width / 2f, height / 2f, -10f);
            Camera = camGo.AddComponent<Camera>();
            Camera.orthographic = true; Camera.orthographicSize = height / 2f;
            Camera.clearFlags = CameraClearFlags.SolidColor; Camera.backgroundColor = Color.black;
            Camera.rect = viewport; Camera.depth = cameraDepth; Camera.nearClipPlane = 0.1f; Camera.farClipPlane = 50f;
            Canvas = Ui.CreateCanvas(name + "_Hud", width, height, Camera, 0);
            Canvas.transform.SetParent(Root.transform, false);
            Canvas.GetComponent<CanvasScaler>().matchWidthOrHeight = 0.5f;
            CanvasRect = (RectTransform)Canvas.transform;
        }

        public Vector3 P(double cx, double cy) => new Vector3((float)cx, (float)(Height - cy), 0f);

        public SpritePool Pool(string key)
        {
            if (!_pools.TryGetValue(key, out var p)) { p = new SpritePool(Root.transform, key); _pools[key] = p; }
            return p;
        }

        public void Begin()
        {
            if (ViewportFn != null) Camera.rect = ViewportFn();
            foreach (var p in _pools.Values) p.Begin();
        }
        public void End() { foreach (var p in _pools.Values) p.End(); }

        /// <summary>Zeichnet ein Pygame-Rechteck (oben links) mit einem Sprite, skaliert auf die Rechteckgröße.</summary>
        public SpriteRenderer DrawRect(string pool, Sprite s, double x, double y, double w, double h, int order, Color color, bool flipX = false, bool flipY = false, float rotZ = 0f)
            => Pool(pool).Draw(s, P(x + w / 2.0, y + h / 2.0), (float)w, (float)h, order, color, flipX, flipY, rotZ);

        public void DrawOutline(string pool, RectI r, Color c, int order = 100)
        {
            var w = SpriteLibrary.White;
            DrawRect(pool, w, r.X, r.Y, r.W, 1, order, c); DrawRect(pool, w, r.X, r.Bottom - 1, r.W, 1, order, c);
            DrawRect(pool, w, r.X, r.Y, 1, r.H, order, c); DrawRect(pool, w, r.Right - 1, r.Y, 1, r.H, order, c);
        }

        public void Destroy()
        {
            if (Camera != null) Object.Destroy(Camera.gameObject);
            if (Root != null) Object.Destroy(Root);
        }
    }

    /// <summary>Zeichnet BackgroundDirector (Sterne, Planeten, Vordergrund, Systemfilter, Karten-Überblendung).</summary>
    public sealed class BackgroundView
    {
        private readonly Stage _stage;
        private readonly RectTransform _transitionPanel;
        private readonly Text _fromText, _toText, _arrivedText, _titleText;
        private readonly Image _dim, _line, _fromCircle, _toCircle, _fromThumb, _toThumb;
        private readonly Text _systemLabel;

        public BackgroundView(Stage stage)
        {
            _stage = stage;
            var canvas = stage.CanvasRect;
            _systemLabel = Ui.LabelAt(canvas, "", new Vector2(0.45f, 0.94f), new Vector2(0.99f, 0.995f), 18, TextAnchor.MiddleRight, new Color(0.8f, 0.85f, 1f, 0.85f));
            _transitionPanel = Ui.Fill(canvas, "Transition");
            _dim = Ui.Background(_transitionPanel, new Color(0, 0, 0, 0));
            _titleText = Ui.LabelAt(_transitionPanel, "GALAXIEKARTE", new Vector2(0.05f, 0.80f), new Vector2(0.95f, 0.90f), 30, TextAnchor.MiddleCenter, Ui.Gold, FontStyle.Bold);
            _line = Ui.Rect(_transitionPanel, "Line", new Vector2(0.18f, 0.5f), new Vector2(0.82f, 0.5f), new Vector2(0, -1), new Vector2(0, 1)).gameObject.AddComponent<Image>();
            _line.color = new Color(0.6f, 0.8f, 1f, 0.7f);
            _fromCircle = Circle(_transitionPanel, new Vector2(0.18f, 0.5f), 34); _toCircle = Circle(_transitionPanel, new Vector2(0.82f, 0.5f), 34);
            _fromThumb = Thumb(_transitionPanel, new Vector2(0.18f, 0.5f), 56); _toThumb = Thumb(_transitionPanel, new Vector2(0.82f, 0.5f), 56);
            _fromText = Ui.LabelAt(_transitionPanel, "", new Vector2(0.0f, 0.34f), new Vector2(0.4f, 0.44f), 22, TextAnchor.MiddleCenter, Color.white, FontStyle.Bold);
            _toText = Ui.LabelAt(_transitionPanel, "", new Vector2(0.6f, 0.34f), new Vector2(1f, 0.44f), 22, TextAnchor.MiddleCenter, Color.white, FontStyle.Bold);
            _arrivedText = Ui.LabelAt(_transitionPanel, "ZIELSYSTEM ERREICHT", new Vector2(0.05f, 0.18f), new Vector2(0.95f, 0.28f), 26, TextAnchor.MiddleCenter, Ui.Good, FontStyle.Bold);
            _transitionPanel.gameObject.SetActive(false);
        }

        private static Image Circle(Transform parent, Vector2 anchor, float size)
        {
            var rt = Ui.Rect(parent, "Circle", anchor, anchor, new Vector2(-size, -size), new Vector2(size, size));
            var img = rt.gameObject.AddComponent<Image>(); img.sprite = SpriteLibrary.Circle; img.color = new Color(0.35f, 0.55f, 0.9f, 0.35f); img.raycastTarget = false; return img;
        }
        private static Image Thumb(Transform parent, Vector2 anchor, float size)
        {
            var rt = Ui.Rect(parent, "Thumb", anchor, anchor, new Vector2(-size / 2, -size / 2), new Vector2(size / 2, size / 2));
            var img = rt.gameObject.AddComponent<Image>(); img.preserveAspect = true; img.raycastTarget = false; img.enabled = false; return img;
        }

        private static void SetThumb(Image img, string[] keys)
        {
            if (keys != null && keys.Length > 0) { img.sprite = SpriteLibrary.Planet(keys[0]); img.enabled = true; } else img.enabled = false;
        }

        public void Draw(BackgroundDirector bg, bool showSystemLabel = true)
        {
            var s = _stage; int W = s.Width, H = s.Height;
            var tint = Color.white;
            var white = SpriteLibrary.White;
            foreach (var p in bg.Planets)
                s.DrawRect("planets", SpriteLibrary.Planet(p.Key), p.X, p.Y, p.Width, p.Height, 0, Color.white);
            foreach (var st in bg.Layer1) s.DrawRect("stars1", white, st.X, st.Y, st.Size, st.Size, 1, new Color32((byte)st.R, (byte)st.G, (byte)st.B, 255));
            foreach (var st in bg.Layer2) s.DrawRect("stars2", white, st.X, st.Y, st.Size, st.Size, 2, new Color32((byte)st.R, (byte)st.G, (byte)st.B, 255));
            var sys = bg.Systems.Current;
            if (sys != null && sys.VisualFilter[3] > 0)
                s.DrawRect("filter", white, 0, 0, W, H, 3, new Color32((byte)sys.VisualFilter[0], (byte)sys.VisualFilter[1], (byte)sys.VisualFilter[2], (byte)sys.VisualFilter[3]));
            foreach (var f in bg.Foreground)
                s.DrawRect("foreground", SpriteLibrary.AsteroidFrame(f.Frame), f.X, f.Y, f.Width, f.Height, 5, new Color32(8, 8, 12, 255));

            _systemLabel.text = showSystemLabel && sys != null ? string.Join("  |  ", sys.DisplayLines) : "";

            bool active = bg.Transition.Active;
            if (_transitionPanel.gameObject.activeSelf != active) _transitionPanel.gameObject.SetActive(active);
            if (active)
            {
                float t = (float)bg.TransitionProgress;
                float fade = Mathf.Clamp01(Mathf.Min(t / 0.12f, (1f - t) / 0.12f));
                _dim.color = new Color(0, 0, 0, 0.6f * fade);
                _fromText.text = bg.Transition.From != null ? bg.Transition.From.IdName : ""; _toText.text = bg.Transition.To != null ? bg.Transition.To.IdName : "";
                SetThumb(_fromThumb, bg.Transition.FromPlanets); SetThumb(_toThumb, bg.Transition.ToPlanets);
                _arrivedText.color = new Color(Ui.Good.r, Ui.Good.g, Ui.Good.b, t > 0.8f ? 1f : 0f);
                float a = fade;
                _titleText.color = new Color(1f, 0.85f, 0.2f, a); _line.color = new Color(0.6f, 0.8f, 1f, 0.7f * a);
                _fromCircle.color = new Color(0.35f, 0.55f, 0.9f, 0.35f * a); _toCircle.color = new Color(0.35f, 0.55f, 0.9f, 0.35f * a);
                _fromText.color = new Color(1, 1, 1, a); _toText.color = new Color(1, 1, 1, a);
            }
        }
    }
}
