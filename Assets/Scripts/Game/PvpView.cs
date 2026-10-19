using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>Einheitliche Darstellungsdaten für lokale/Host-Welt (PvpWorld) und Client-Ansicht (PvpClientView).</summary>
    public sealed class PvpFrame
    {
        public sealed class P { public string Id, Name, Ship, Role; public double X, Y; public int W, H, Score, Lives; public bool Alive, Eliminated, Invulnerable, Blink = true; }
        public sealed class A { public double X, Y; public int W, H, Frame; }
        public sealed class Pr { public string Weapon, OwnerId; public double X, Y; public int W, H; }
        public sealed class Fx { public double X, Y, Scale; }
        public readonly List<P> Players = new List<P>();
        public readonly List<A> Asteroids = new List<A>();
        public readonly List<Pr> Projectiles = new List<Pr>();
        public readonly List<Fx> Effects = new List<Fx>();
        public BackgroundDirector Background;
        public string Mode; public int ElapsedMs; public bool Over; public Dictionary<string, object> Result;

        public static PvpFrame From(PvpWorld w)
        {
            var f = new PvpFrame { Background = w.Background, Mode = w.Mode, ElapsedMs = w.MatchElapsedMs, Over = w.MatchOver, Result = w.Result };
            foreach (var p in w.Players)
                f.Players.Add(new P { Id = p.Id, Name = p.Name, Ship = p.ShipKey, Role = p.Role, X = p.Ship.X, Y = p.Ship.Y, W = p.Ship.Width, H = p.Ship.Height, Score = p.Score, Lives = p.Ship.Lives,
                    Alive = p.Alive, Eliminated = p.Eliminated, Invulnerable = p.Ship.IsInvulnerable, Blink = p.RespawnAtMs <= 0 && p.Ship.BlinkVisible() });
            foreach (var a in w.Asteroids.Values) f.Asteroids.Add(new A { X = a.X, Y = a.Y, W = a.Width, H = a.Height, Frame = a.Frame });
            foreach (var pr in w.Projectiles) f.Projectiles.Add(new Pr { Weapon = pr.Weapon, OwnerId = pr.OwnerId, X = pr.Obj.Rect.X, Y = pr.Obj.Rect.Y, W = pr.Obj.Rect.W, H = pr.Obj.Rect.H });
            foreach (var e in w.Effects.Values) if (w.Clock.NowMs - e.CreatedAtMs <= GameConstants.PvpExplosionDurationMs) f.Effects.Add(new Fx { X = e.X, Y = e.Y, Scale = e.Scale });
            return f;
        }

        public static PvpFrame From(PvpClientView v)
        {
            var f = new PvpFrame { Background = v.Background, Mode = v.Mode, ElapsedMs = v.MatchElapsedMs, Over = v.MatchOver, Result = v.Result };
            foreach (var id in v.PlayerOrder)
            {
                var p = v.Players[id];
                f.Players.Add(new P { Id = p.Id, Name = p.Name, Ship = p.Ship, Role = p.Role, X = p.X, Y = p.Y, W = p.Width, H = p.Height, Score = p.Score, Lives = p.Lives, Alive = p.Alive, Eliminated = p.Eliminated,
                    Invulnerable = p.Invulnerable, Blink = !p.Invulnerable || ((long)v.Clock.NowMs / GameConstants.InvulnerableBlinkMs) % 2 == 0 });
            }
            foreach (var a in v.Asteroids) f.Asteroids.Add(new A { X = a.X, Y = a.Y, W = a.Width, H = a.Height, Frame = a.Frame });
            foreach (var pr in v.Projectiles) f.Projectiles.Add(new Pr { Weapon = pr.Weapon, OwnerId = pr.OwnerId, X = pr.X, Y = pr.Y, W = pr.Width, H = pr.Height });
            foreach (var e in v.Effects.Values) f.Effects.Add(new Fx { X = e.X, Y = e.Y, Scale = e.Scale });
            return f;
        }
    }

    /// <summary>
    /// Darstellung des PvP-Duells (800x600). Die eigene Rolle ("bottom"/"top") bestimmt die Perspektive: Der lokale Spieler
    /// steht immer unten; bei Rolle "top" wird die Welt vertikal gespiegelt, gegnerische Schiffe/Projektile erscheinen gedreht.
    /// </summary>
    public sealed class PvpView
    {
        public readonly Stage Stage;
        private readonly BackgroundView _bg;
        private readonly Text _topBar, _bottomBar, _centerText, _timer;

        public PvpView(Stage stage)
        {
            Stage = stage;
            _bg = new BackgroundView(stage);
            _topBar = Ui.LabelAt(stage.CanvasRect, "", new Vector2(0.01f, 0.93f), new Vector2(0.99f, 1f), 24, TextAnchor.MiddleLeft, Color.white, FontStyle.Bold);
            _bottomBar = Ui.LabelAt(stage.CanvasRect, "", new Vector2(0.01f, 0f), new Vector2(0.99f, 0.07f), 24, TextAnchor.MiddleLeft, Color.white, FontStyle.Bold);
            _timer = Ui.LabelAt(stage.CanvasRect, "", new Vector2(0.4f, 0.93f), new Vector2(0.6f, 1f), 26, TextAnchor.MiddleCenter, Ui.Gold, FontStyle.Bold);
            _centerText = Ui.LabelAt(stage.CanvasRect, "", new Vector2(0.1f, 0.4f), new Vector2(0.9f, 0.6f), 36, TextAnchor.MiddleCenter, Ui.Gold, FontStyle.Bold);
        }

        public void SetCenterText(string t) { _centerText.text = t ?? ""; }

        private double Vy(double y, double h, bool mirror) => mirror ? Stage.Height - y - h : y;

        public void Draw(PvpFrame f, string localRole)
        {
            var s = Stage; bool mirror = localRole == "top";
            s.Begin();
            _bg.Draw(f.Background);
            foreach (var a in f.Asteroids) s.DrawRect("asteroids", SpriteLibrary.AsteroidFrame(a.Frame), a.X, Vy(a.Y, a.H, mirror), a.W, a.H, 10, Color.white);
            foreach (var pr in f.Projectiles)
            {
                var owner = f.Players.Find(p => p.Id == pr.OwnerId);
                bool flip = owner != null && owner.Role != localRole;
                double y = Vy(pr.Y, pr.H, mirror);
                if (pr.Weapon == "torpedo") s.DrawRect("torpedoes", SpriteLibrary.Torpedo, pr.X, y, pr.W, pr.H, 11, Color.white, false, flip);
                else s.DrawRect("lasers", SpriteLibrary.White, pr.X, y, pr.W, pr.H, 11, flip ? new Color(1f, 0.6f, 0.1f) : new Color(1f, 0.15f, 0.15f));
            }
            foreach (var p in f.Players)
            {
                if (p.Eliminated || !p.Alive || !p.Blink) continue;
                bool opponent = p.Role != localRole;
                bool tie = p.Ship == "tiefighter";
                // Original: gegnerische Schiffe werden vertikal gespiegelt dargestellt (Tie ist bereits um 180° gedreht).
                s.DrawRect("players", SpriteLibrary.Ship(p.Ship), p.X, Vy(p.Y, p.H, mirror), p.W, p.H, 20, Color.white, tie, tie ^ opponent);
            }
            foreach (var e in f.Effects)
            {
                int w = PyMath.ScaleDim(AssetMetrics.ExplosionBaseWidth, e.Scale * 0.5), h = PyMath.ScaleDim(AssetMetrics.ExplosionBaseHeight, e.Scale * 0.5);
                s.DrawRect("fx", SpriteLibrary.Explosion, e.X - w / 2.0, Vy(e.Y - h / 2.0, h, mirror), w, h, 30, Color.white);
            }
            s.End();

            var local = f.Players.Find(p => p.Role == localRole); var other = f.Players.Find(p => p.Role != localRole);
            string Fmt(PvpFrame.P p) => p == null ? "" : $"{p.Name}   Punkte: {p.Score}   Leben: {Mathf.Max(0, p.Lives)}";
            _topBar.text = Fmt(other); _bottomBar.text = Fmt(local);
            if (f.Mode == PvpModes.Points)
            {
                int left = Mathf.Max(0, (GameConstants.PvpScoreLimitMs - f.ElapsedMs) / 1000);
                _timer.text = $"{left / 60}:{left % 60:00}";
            }
            else _timer.text = "";
        }
    }
}
