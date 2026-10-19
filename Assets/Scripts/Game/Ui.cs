using System;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace StarWars.Game
{
    /// <summary>Kleine uGUI-Hilfsbibliothek: baut Canvas, Texte, Buttons und Eingabefelder per Code (keine manuelle Szeneneinrichtung nötig).</summary>
    public static class Ui
    {
        public static readonly Color Gold = new Color(1f, 0.85f, 0.2f), Panel = new Color(0.05f, 0.07f, 0.14f, 0.88f),
            ButtonColor = new Color(0.12f, 0.2f, 0.38f, 0.95f), ButtonHover = new Color(0.2f, 0.34f, 0.6f, 1f), Dim = new Color(0, 0, 0, 0.6f),
            Danger = new Color(0.85f, 0.2f, 0.2f), Good = new Color(0.3f, 0.9f, 0.4f), Grey = new Color(0.7f, 0.74f, 0.8f);

        private static Font _font;
        public static Font DefaultFont
        {
            get
            {
                if (_font != null) return _font;
                _font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                if (_font == null) _font = Font.CreateDynamicFontFromOSFont("Arial", 16);
                return _font;
            }
        }

        public static void EnsureEventSystem()
        {
            if (UnityEngine.Object.FindFirstObjectByType<EventSystem>() != null) return;
            var go = new GameObject("EventSystem");
            go.AddComponent<EventSystem>();
#if ENABLE_LEGACY_INPUT_MANAGER
            go.AddComponent<StandaloneInputModule>();
#endif
        }

        /// <summary>Overlay-Canvas (oder Kamera-Canvas), skaliert mit der Bildschirmgröße.</summary>
        public static Canvas CreateCanvas(string name, int refW, int refH, Camera cam = null, int sortingOrder = 0)
        {
            EnsureEventSystem();
            var go = new GameObject(name);
            var canvas = go.AddComponent<Canvas>();
            if (cam == null) canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            else { canvas.renderMode = RenderMode.ScreenSpaceCamera; canvas.worldCamera = cam; canvas.planeDistance = 10f; }
            canvas.sortingOrder = sortingOrder;
            var scaler = go.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(refW, refH);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;
            go.AddComponent<GraphicRaycaster>();
            return canvas;
        }

        public static RectTransform Rect(Transform parent, string name, Vector2 anchorMin, Vector2 anchorMax, Vector2 offMin, Vector2 offMax)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rt = (RectTransform)go.transform;
            rt.SetParent(parent, false);
            rt.anchorMin = anchorMin; rt.anchorMax = anchorMax; rt.offsetMin = offMin; rt.offsetMax = offMax;
            return rt;
        }

        public static RectTransform Fill(Transform parent, string name) => Rect(parent, name, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);

        public static Image Background(Transform parent, Color color, string name = "Background")
        {
            var rt = Fill(parent, name);
            var img = rt.gameObject.AddComponent<Image>(); img.color = color; img.raycastTarget = false;
            return img;
        }

        public static Image Picture(Transform parent, Sprite sprite, Vector2 size, string name = "Image")
        {
            var rt = Rect(parent, name, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), -size / 2f, size / 2f);
            var img = rt.gameObject.AddComponent<Image>(); img.sprite = sprite; img.preserveAspect = true; img.raycastTarget = false;
            return img;
        }

        public static Text Label(Transform parent, string text, int size = 24, TextAnchor anchor = TextAnchor.MiddleCenter, Color? color = null, FontStyle style = FontStyle.Normal, string name = "Text")
        {
            var rt = Fill(parent, name);
            var t = rt.gameObject.AddComponent<Text>();
            t.font = DefaultFont; t.text = text; t.fontSize = size; t.alignment = anchor; t.color = color ?? Color.white; t.fontStyle = style;
            t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow; t.raycastTarget = false;
            return t;
        }

        /// <summary>Text mit festen Ankern (Prozentwerte) im Elternobjekt.</summary>
        public static Text LabelAt(Transform parent, string text, Vector2 anchorMin, Vector2 anchorMax, int size = 24, TextAnchor anchor = TextAnchor.MiddleCenter, Color? color = null, FontStyle style = FontStyle.Normal)
        {
            var rt = Rect(parent, "Text", anchorMin, anchorMax, Vector2.zero, Vector2.zero);
            var t = rt.gameObject.AddComponent<Text>();
            t.font = DefaultFont; t.text = text; t.fontSize = size; t.alignment = anchor; t.color = color ?? Color.white; t.fontStyle = style;
            t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow; t.raycastTarget = false;
            return t;
        }

        public static Button MakeButton(Transform parent, string label, UnityAction onClick, string name = "Button", int fontSize = 26)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(parent, false);
            var img = go.GetComponent<Image>(); img.color = ButtonColor;
            var btn = go.GetComponent<Button>();
            var colors = btn.colors; colors.normalColor = Color.white; colors.highlightedColor = new Color(1.4f, 1.4f, 1.6f, 1f); colors.pressedColor = new Color(0.7f, 0.7f, 0.8f, 1f); colors.selectedColor = Color.white;
            btn.colors = colors; btn.targetGraphic = img;
            if (onClick != null) btn.onClick.AddListener(() => { SoundBank.Play(Sfx.Click); onClick(); });
            Label(go.transform, label, fontSize, TextAnchor.MiddleCenter, Color.white, FontStyle.Bold);
            return btn;
        }

        public static InputField MakeInput(Transform parent, string initial, string placeholder, int maxLen, bool digitsOnly = false)
        {
            var go = new GameObject("InputField", typeof(RectTransform), typeof(Image), typeof(InputField));
            go.transform.SetParent(parent, false);
            go.GetComponent<Image>().color = new Color(0.02f, 0.03f, 0.08f, 1f);
            var field = go.GetComponent<InputField>();
            var text = Label(go.transform, "", 24, TextAnchor.MiddleLeft, Color.white);
            ((RectTransform)text.transform).offsetMin = new Vector2(12, 4); ((RectTransform)text.transform).offsetMax = new Vector2(-12, -4);
            text.raycastTarget = true;
            var ph = Label(go.transform, placeholder, 22, TextAnchor.MiddleLeft, new Color(1, 1, 1, 0.35f), FontStyle.Italic, "Placeholder");
            ((RectTransform)ph.transform).offsetMin = new Vector2(12, 4); ((RectTransform)ph.transform).offsetMax = new Vector2(-12, -4);
            field.textComponent = text; field.placeholder = ph; field.characterLimit = maxLen; field.text = initial ?? "";
            if (digitsOnly) field.onValidateInput += (s, i, c) => (char.IsDigit(c) || c == '.') ? c : '\0';
            return field;
        }

        /// <summary>Vertikale Spalte (Menü) mit fester Breite in der Bildschirmmitte.</summary>
        public static RectTransform Column(Transform parent, float width, float spacing = 12f, TextAnchor align = TextAnchor.MiddleCenter, float yOffset = 0f)
        {
            var rt = Rect(parent, "Column", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(-width / 2f, -400), new Vector2(width / 2f, 400));
            rt.anchoredPosition = new Vector2(0, yOffset);
            var v = rt.gameObject.AddComponent<VerticalLayoutGroup>();
            v.childAlignment = align; v.spacing = spacing; v.childControlWidth = true; v.childControlHeight = true; v.childForceExpandWidth = true; v.childForceExpandHeight = false;
            return rt;
        }

        public static T Sized<T>(T comp, float height) where T : Component
        {
            var le = comp.gameObject.GetComponent<LayoutElement>() ?? comp.gameObject.AddComponent<LayoutElement>();
            le.preferredHeight = height; le.minHeight = height;
            return comp;
        }

        public static Text Line(Transform column, string text, int size = 24, Color? color = null, float height = 36f, FontStyle style = FontStyle.Normal, TextAnchor anchor = TextAnchor.MiddleCenter)
        {
            var go = new GameObject("Line", typeof(RectTransform)); go.transform.SetParent(column, false);
            var t = Label(go.transform, text, size, anchor, color, style);
            var le = go.AddComponent<LayoutElement>(); le.preferredHeight = height; le.minHeight = height;
            return t;
        }

        public static Button Btn(Transform column, string label, UnityAction onClick, float height = 56f, int font = 26)
        {
            var b = MakeButton(column, label, onClick, "Button", font);
            Sized(b, height); return b;
        }

        public static void Spacer(Transform column, float height)
        {
            var go = new GameObject("Spacer", typeof(RectTransform)); go.transform.SetParent(column, false);
            var le = go.AddComponent<LayoutElement>(); le.preferredHeight = height; le.minHeight = height;
        }

        public static void Destroy(UnityEngine.Object o) { if (o != null) UnityEngine.Object.Destroy(o); }
    }

    /// <summary>Normalisierte Viewport-Rechtecke für ein 4:3-Spielfeld (Letterbox) – unabhängig von der Fensterauflösung.</summary>
    public static class Letterbox
    {
        public static Rect Fit(float aspect = 800f / 600f)
        {
            float screenAspect = Screen.height > 0 ? (float)Screen.width / Screen.height : aspect;
            if (screenAspect > aspect) { float w = aspect / screenAspect; return new Rect((1f - w) / 2f, 0f, w, 1f); }
            float h = screenAspect / aspect; return new Rect(0f, (1f - h) / 2f, 1f, h);
        }

        public static Rect Sub(Rect outer, float x, float w) => new Rect(outer.x + outer.width * x, outer.y, outer.width * w, outer.height);
    }
}
