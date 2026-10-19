using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>Zeichnet eine <see cref="SinglePlayerWorld"/> (Einzelspieler, jede Punktekampf-Welt, LAN-Punktekampf) samt HUD.</summary>
    public sealed class WorldView
    {
        public readonly Stage Stage;
        private readonly BackgroundView _bg;
        private readonly Text _score, _extra;
        private readonly List<Image> _lives = new List<Image>();
        private readonly RectTransform _warning;
        private readonly Text _warningText;
        private readonly List<Text> _ghostLabels = new List<Text>();
        private int _ghostUsed;
        public bool ShowHitbox;
        private bool _rebels;

        public WorldView(Stage stage, bool rebels)
        {
            Stage = stage; _rebels = rebels;
            _bg = new BackgroundView(stage);
            _score = Ui.LabelAt(stage.CanvasRect, "Punkte: 0", new Vector2(0.01f, 0.93f), new Vector2(0.7f, 1f), 36, TextAnchor.UpperLeft, Color.white, FontStyle.Bold);
            _extra = Ui.LabelAt(stage.CanvasRect, "", new Vector2(0.01f, 0.86f), new Vector2(0.99f, 0.93f), 20, TextAnchor.UpperLeft, new Color(1, 1, 1, 0.8f));
            _warning = Ui.Rect(stage.CanvasRect, "Warning", new Vector2(0f, 0.38f), new Vector2(1f, 0.62f), Vector2.zero, Vector2.zero);
            Ui.Background(_warning, new Color(0.47f, 0f, 0f, 0.37f));
            Ui.LabelAt(_warning, "!!! WARNUNG !!!", new Vector2(0, 0.5f), new Vector2(1, 1), 40, TextAnchor.LowerCenter, new Color(1f, 0.35f, 0.3f), FontStyle.Bold);
            _warningText = Ui.LabelAt(_warning, "", new Vector2(0.03f, 0), new Vector2(0.97f, 0.5f), 24, TextAnchor.UpperCenter, Color.white);
            _warning.gameObject.SetActive(false);
        }

        public void SetFaction(bool rebels) { _rebels = rebels; }
        public void SetExtraText(string t) { _extra.text = t; }

        private void EnsureLives(int n)
        {
            while (_lives.Count < 3)
            {
                int i = _lives.Count;
                var rt = Ui.Rect(Stage.CanvasRect, "Life" + i, new Vector2(0, 1), new Vector2(0, 1), Vector2.zero, Vector2.zero);
                rt.pivot = new Vector2(0, 1); rt.anchoredPosition = new Vector2(6, -(42 + i * 28)); rt.sizeDelta = new Vector2(72, 24);
                var img = rt.gameObject.AddComponent<Image>(); img.raycastTarget = false; img.preserveAspect = false;
                _lives.Add(img);
            }
            var sprite = SpriteLibrary.Lightsaber(_rebels);
            for (int i = 0; i < _lives.Count; i++) { _lives[i].sprite = sprite; _lives[i].gameObject.SetActive(i < n); }
        }

        public void Draw(SinglePlayerWorld w)
        {
            var s = Stage;
            s.Begin(); _ghostUsed = 0;
            _bg.Draw(w.Background);

            foreach (var a in w.Asteroids) s.DrawRect("asteroids", SpriteLibrary.AsteroidFrame(a.Frame), a.X, a.Y, a.Width, a.Height, 10, Color.white);
            foreach (var l in w.Lasers) s.DrawRect("lasers", SpriteLibrary.White, l.Rect.X, l.Rect.Y, l.Rect.W, l.Rect.H, 11, new Color(1f, 0.15f, 0.15f));
            foreach (var t in w.Torpedoes) s.DrawRect("torpedoes", SpriteLibrary.Torpedo, t.Rect.X, t.Rect.Y, t.Rect.W, t.Rect.H, 11, Color.white);

            foreach (var e in w.Enemies.Enemies)
            {
                bool flash = e.DamageFlashTimer > 0;
                s.DrawRect("enemies", SpriteLibrary.Ship(e.ShipKey), PyMath.Round(e.X), PyMath.Round(e.Y), e.Width, e.Height, 12, flash ? new Color(1f, 0.55f, 0.55f) : Color.white, true, true);
                double ratio = e.MaxHp > 0 ? (double)e.Hp / e.MaxHp : 0;
                s.DrawRect("hpbg", SpriteLibrary.White, e.X + e.Width * 0.1, e.Y - 8, e.Width * 0.8, 5, 13, new Color(0.15f, 0.15f, 0.15f, 0.9f));
                s.DrawRect("hpfill", SpriteLibrary.White, e.X + e.Width * 0.1, e.Y - 8, e.Width * 0.8 * ratio, 5, 14, Color.Lerp(Ui.Danger, Ui.Good, (float)ratio));
                if (ShowHitbox) s.DrawOutline("dbg", e.Hitbox, Color.yellow);
            }
            foreach (var p in w.Enemies.Projectiles)
            {
                if (p.IsTorpedo)
                {
                    float ang = Mathf.Atan2((float)p.Vy, (float)p.Vx) * Mathf.Rad2Deg + 90f;
                    s.DrawRect("etorp", SpriteLibrary.Torpedo, p.Rect.X, p.Rect.Y, p.Rect.W, p.Rect.H, 12, new Color(1f, 0.6f, 0.3f), false, false, -ang + 180f);
                }
                else s.DrawRect("elaser", SpriteLibrary.White, p.Rect.X, p.Rect.Y, p.Rect.W, p.Rect.H, 12, new Color(1f, 0.55f, 0.1f));
            }

            if (!w.Dead && w.Player.BlinkVisible())
            {
                var pl = w.Player; bool tie = pl.Info.Key == "tiefighter";
                s.DrawRect("player", SpriteLibrary.Ship(pl.Info.Key), pl.X, pl.Y, pl.Width, pl.Height, 20, Color.white, tie, tie);
            }
            if (ShowHitbox)
            {
                s.DrawOutline("dbg", w.Player.Hitbox, Color.green);
                foreach (var a in w.Asteroids) s.DrawOutline("dbg", a.GetRect(), Color.cyan);
            }

            foreach (var ex in w.Explosions) DrawExplosion(ex);
            foreach (var ex in w.Enemies.Explosions) DrawExplosion(ex);
            s.End();

            _score.text = "Punkte: " + w.Score;
            EnsureLives(w.Dead ? 0 : w.Player.Lives);
            bool warn = !string.IsNullOrEmpty(w.WarningText);
            if (_warning.gameObject.activeSelf != warn) _warning.gameObject.SetActive(warn);
            if (warn) _warningText.text = w.WarningText;
        }

        private void DrawExplosion(Explosion ex)
        {
            var r = ex.Rect;
            Stage.DrawRect("explosions", SpriteLibrary.Explosion, r.X, r.Y, r.W, r.H, 30, Color.white);
        }

        /// <summary>Halbtransparenter Ghost eines Mitspielers (nur Anzeige). Aufruf zwischen Draw()-Aufrufen im selben Frame.</summary>
        public void DrawGhost(string shipKey, double nx, double ny, string label)
        {
            var m = AssetMetrics.Ships[shipKey];
            double x = nx * Stage.Width - m.Width / 2.0, y = ny * Stage.Height;
            bool tie = shipKey == "tiefighter";
            Stage.DrawRect("ghost", SpriteLibrary.Ship(shipKey), x, y, m.Width, m.Height, 18, new Color(1f, 1f, 1f, 105f / 255f), tie, tie);
            if (_ghostUsed >= _ghostLabels.Count)
            {
                var t = Ui.LabelAt(Stage.CanvasRect, "", Vector2.zero, Vector2.one, 16, TextAnchor.UpperLeft, new Color(1, 1, 1, 0.8f));
                _ghostLabels.Add(t);
            }
            var lab = _ghostLabels[_ghostUsed++]; lab.gameObject.SetActive(true); lab.text = label;
            var rt = (RectTransform)lab.transform; rt.anchorMin = new Vector2(0, 1); rt.anchorMax = new Vector2(0, 1); rt.pivot = new Vector2(0.5f, 1f);
            rt.sizeDelta = new Vector2(260, 24); rt.anchoredPosition = new Vector2((float)(x + m.Width / 2.0), -(float)(y - 22));
        }

        public void BeginGhosts() { Stage.Pool("ghost").Begin(); _ghostUsed = 0; }

        public void EndGhosts() { Stage.Pool("ghost").End(); for (int i = _ghostUsed; i < _ghostLabels.Count; i++) _ghostLabels[i].gameObject.SetActive(false); }
    }
}
