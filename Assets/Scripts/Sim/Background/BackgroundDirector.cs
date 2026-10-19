using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>game/background/objects.py – Star.</summary>
    public sealed class Star
    {
        public double X, Y, Speed;
        public int Layer, Size, BrightnessMin, BrightnessMax, BrightnessChange;
        public int R, G, B;
        public bool Twinkle;
        private readonly int _w, _h;
        private readonly ISimRandom _rng;

        public Star(int width, int height, int layer, int[] tint, ISimRandom rng)
        {
            _w = width; _h = height; Layer = layer; _rng = rng;
            X = rng.Uniform(0, width); Y = rng.Uniform(0, height);
            double baseSpeed;
            if (layer == 1) { Size = 1; baseSpeed = 0.12; BrightnessMin = 110; BrightnessMax = 220; }
            else if (layer == 2) { Size = rng.Choice(1, 2, 2, 3); baseSpeed = 0.35; BrightnessMin = 140; BrightnessMax = 255; }
            else { Size = rng.Choice(2, 3, 4); baseSpeed = 0.7; BrightnessMin = 180; BrightnessMax = 255; }
            Speed = baseSpeed * (Size / 1.5) * (0.6 + rng.NextDouble());
            int brightness = rng.Int(BrightnessMin, BrightnessMax);
            if (layer == 2 && rng.NextDouble() < 0.3)
            {
                int[] t = tint ?? (rng.NextDouble() < 0.5 ? new[] { 180, 200, 255 } : new[] { 255, 200, 200 });
                R = Math.Min(255, brightness * t[0] / 255); G = Math.Min(255, brightness * t[1] / 255); B = Math.Min(255, brightness * t[2] / 255);
            }
            else { R = G = B = brightness; }
            Twinkle = rng.NextDouble() < 0.25;
            BrightnessChange = Twinkle ? rng.Choice(-1, 1) : 0;
        }

        public void Update()
        {
            Y += Speed;
            if (Twinkle)
            {
                int step = _rng.Int(0, 3);
                int r = R + BrightnessChange * step;
                if (r > BrightnessMax) { r = BrightnessMax; BrightnessChange = -1; }
                else if (r < BrightnessMin) { r = BrightnessMin; BrightnessChange = 1; }
                R = G = B = r;
            }
            if (Y > _h) { Y = -Size - 2; X = _rng.Uniform(0, _w); }
        }
    }

    /// <summary>game/background/objects.py – Planet (Position/Größe in Pixeln).</summary>
    public sealed class PlanetObject
    {
        public string Key;
        public double X, Y, Speed, DriftX;
        public int Width, Height;
        public bool IsExiting;
        public RectI Rect => new RectI((int)X, (int)Y, Width, Height);

        public PlanetObject(string key, int sceneWidth, ISimRandom rng, double speedMin, double speedMax)
        {
            Key = key;
            var size = PlanetCatalog.Size(key);
            double scale = rng.Uniform(0.35, 0.7);
            Width = Math.Max(16, (int)(size[0] * scale)); Height = Math.Max(16, (int)(size[1] * scale));
            X = rng.Uniform(50, Math.Max(50, sceneWidth - Width - 50));
            Y = -Height;
            Speed = rng.Uniform(speedMin, speedMax);
            DriftX = rng.Uniform(-0.15, 0.15);
        }

        public void Update()
        {
            if (IsExiting) { Y += Speed * 4.0; X += DriftX * 2; return; }
            Y += Speed; X += DriftX;
        }

        public bool Expired(int sceneHeight) => Y > sceneHeight + Height;
    }

    /// <summary>game/background/objects.py – ForegroundObject (dunkle Silhouette eines Asteroiden-Frames).</summary>
    public sealed class ForegroundObject
    {
        public double X, Y, Speed, DriftX;
        public int Width, Height, Frame;
        public ForegroundObject(int sceneWidth, ISimRandom rng)
        {
            double scale = rng.Uniform(0.5, 1.8);
            Width = Math.Max(6, (int)(AssetMetrics.AsteroidFrameSize * scale)); Height = Width;
            Frame = rng.Int(0, AssetMetrics.AsteroidFrameCount - 1);
            X = rng.Int(0, Math.Max(0, sceneWidth - Width));
            Y = -Height;
            Speed = rng.Uniform(1.8, 3.5);
            DriftX = rng.Uniform(-0.6, 0.6);
        }
        public void Update() { Y += Speed; X += DriftX; }
        public bool Expired(int sceneHeight) => Y > sceneHeight;
    }

    /// <summary>Zustand der Karten-Überblendung beim Systemwechsel (game/background/transition_manager.py), nur Daten – die Darstellung macht die Unity-Schicht.</summary>
    public sealed class TransitionState
    {
        public bool Active;
        public double StartMs;
        public StarSystem From, To;
        public int TargetOrderIndex;
        public int DurationMs;
        public string[] FromPlanets = new string[0], ToPlanets = new string[0];
    }

    /// <summary>
    /// Koordinator des Hintergrunds (game/background/manager.py, starfield.py, planet_manager.py, system_manager.py).
    /// Zeit kommt aus der Simulationsuhr; ein Systemwechsel wird am Ende von Update abgeschlossen
    /// (im Original geschah das im draw-Aufruf desselben Frames).
    /// </summary>
    public sealed class BackgroundDirector
    {
        public readonly int Width, Height;
        public readonly bool AutoSwitch;
        public readonly SystemManager Systems;
        public readonly List<Star> Layer1 = new List<Star>(), Layer2 = new List<Star>();
        public readonly List<PlanetObject> Planets = new List<PlanetObject>();
        public readonly List<ForegroundObject> Foreground = new List<ForegroundObject>();
        public readonly TransitionState Transition = new TransitionState();
        public int SwitchPoints = GameConstants.SystemSwitchPoints;
        public int SwitchTimeMs = GameConstants.SystemSwitchTimeMs;
        public event Action<StarSystem> SystemChanged;

        private readonly SimClock _clock;
        private readonly ISimRandom _rng;
        private double _density = 1.0;
        private int[] _tint;
        private double _lastSwitchMs, _systemEnterMs;
        private int _lastScoreAtSwitch;
        private string[] _planetPool = new string[0];
        private int _spawnCooldown;
        private bool _planetSpawned;
        private int _foregroundCooldown;

        public BackgroundDirector(int width, int height, SimClock clock, ISimRandom rng, bool autoSwitch = true)
        {
            Width = width; Height = height; _clock = clock; _rng = rng; AutoSwitch = autoSwitch;
            Systems = new SystemManager(rng);
            _lastSwitchMs = clock.NowMs; _systemEnterMs = clock.NowMs;
            var cur = Systems.Current;
            _density = cur != null ? cur.StarDensity : 1.0; _tint = cur?.StarTint;
            InitStars();
            ApplySystemVisuals();
        }

        // --- Sterne ---------------------------------------------------------------------------
        private void InitStars()
        {
            double d = Math.Max(0.1, _density);
            int d1 = Math.Max(50, (int)(Width * Height / 6000.0 * d));
            int d2 = Math.Max(20, (int)(Width * Height / 12000.0 * d));
            Layer1.Clear(); Layer2.Clear();
            for (int i = 0; i < d1; i++) Layer1.Add(new Star(Width, Height, 1, null, _rng));
            for (int i = 0; i < d2; i++) Layer2.Add(new Star(Width, Height, 2, _tint, _rng));
        }

        private void ApplySystemVisuals()
        {
            var sys = Systems.Current;
            if (sys == null) return;
            bool changed = Math.Abs(_density - sys.StarDensity) > 1e-6 || !SameTint(_tint, sys.StarTint);
            _density = sys.StarDensity; _tint = sys.StarTint;
            if (changed) InitStars();
            // Planetenpool: eigene Planeten des Systems, sonst alle 13 entdeckten (Original-Fallback).
            _planetPool = sys.PlanetKeys.Length > 0 ? sys.PlanetKeys : PlanetCatalog.AllKeys();
            _spawnCooldown = 0; _planetSpawned = false;
        }

        private static bool SameTint(int[] a, int[] b)
        {
            if (a == null || b == null) return a == b;
            return a[0] == b[0] && a[1] == b[1] && a[2] == b[2];
        }

        // --- Öffentliche Abfragen --------------------------------------------------------------
        public string CurrentSystemName => Systems.CurrentId;
        public int SystemIndex => Systems.OrderIndex;

        /// <summary>get_current_difficulty(): Systemfortschritt für Asteroiden/Gegner.</summary>
        public double SystemBonus => Difficulties.SystemBonus(Systems.OrderIndex);
        public double AsteroidSpeedMultiplier => Systems.Current != null ? Systems.Current.AsteroidSpeedMul : 1.0;

        public void NotifyScoreAnchor(int score) { _lastScoreAtSwitch = score; _lastSwitchMs = _clock.NowMs; }

        // --- Synchronisation für PvP-Clients ----------------------------------------------------
        public void SetSystemOrderByIds(IList<string> ids) { Systems.SetOrderByIds(ids); ApplySystemVisuals(); }

        public void SyncToSystemIndex(int index)
        {
            Systems.AdvanceToIndex(index);
            ApplySystemVisuals();
            Planets.Clear(); Foreground.Clear();
            _systemEnterMs = _clock.NowMs; _lastSwitchMs = _clock.NowMs;
        }

        public void StartSynchronizedTransition(int targetIndex, int elapsedMs, int durationMs)
        {
            if (Systems.Order.Count == 0) return;
            var current = Systems.Current;
            var target = Systems.Order[((targetIndex % Systems.Order.Count) + Systems.Order.Count) % Systems.Order.Count];
            foreach (var p in Planets) { p.IsExiting = true; p.Speed = Math.Max(p.Speed, 2.0); }
            BeginTransition(current, target, targetIndex, durationMs);
            Transition.StartMs = _clock.NowMs - Math.Max(0, elapsedMs);
        }

        // --- Systemwechsel ----------------------------------------------------------------------
        private void BeginTransition(StarSystem from, StarSystem to, int targetIndex, int durationMs)
        {
            Transition.Active = true;
            Transition.StartMs = _clock.NowMs;
            Transition.From = from; Transition.To = to;
            Transition.TargetOrderIndex = targetIndex;
            Transition.DurationMs = durationMs;
            Transition.FromPlanets = from != null ? from.PlanetKeys : new string[0];
            Transition.ToPlanets = to != null ? to.PlanetKeys : new string[0];
        }

        public double TransitionProgress
            => Transition.Active ? PyMath.Clamp((_clock.NowMs - Transition.StartMs) / Math.Max(1.0, Transition.DurationMs), 0.0, 1.0) : 0.0;

        private void RequestSwitchIfNeeded(int score)
        {
            double now = _clock.NowMs;
            double timeElapsed = now - _lastSwitchMs;
            int scoreDiff = score - _lastScoreAtSwitch;
            if (Transition.Active) return;
            if (scoreDiff >= SwitchPoints || timeElapsed >= SwitchTimeMs)
            {
                int nextIdx = Systems.NextIndex;
                var to = Systems.Target; var from = Systems.Current;
                foreach (var p in Planets) { p.IsExiting = true; p.Speed = Math.Max(p.Speed, 2.0); }
                _lastSwitchMs = now; _lastScoreAtSwitch = score;
                BeginTransition(from, to, nextIdx, GameConstants.GalaxyMapDurationMs);
            }
        }

        private void CompleteTransition()
        {
            Systems.MarkVisitedCurrent();
            Systems.AdvanceToIndex(Transition.TargetOrderIndex);
            ApplySystemVisuals();
            Planets.Clear(); _planetSpawned = false; _spawnCooldown = 0;
            Foreground.Clear();
            _lastSwitchMs = _clock.NowMs; _systemEnterMs = _clock.NowMs;
            SystemChanged?.Invoke(Systems.Current);
        }

        // --- Tick -------------------------------------------------------------------------------
        public void Update(int score)
        {
            if (AutoSwitch) RequestSwitchIfNeeded(score);

            foreach (var s in Layer1) s.Update();
            foreach (var s in Layer2) s.Update();

            double now = _clock.NowMs;
            double systemTime = now - _systemEnterMs;
            double timeUntilSwitch = SwitchTimeMs - (now - _lastSwitchMs);
            bool allowPlanets = systemTime > GameConstants.SystemEntryDelayMs && timeUntilSwitch > GameConstants.SystemExitDelayMs;
            MaybeSpawnPlanet(allowPlanets);
            for (int i = Planets.Count - 1; i >= 0; i--)
            {
                Planets[i].Update();
                if (Planets[i].Expired(Height)) Planets.RemoveAt(i);
            }

            if (_foregroundCooldown <= 0 && _rng.NextDouble() < 0.18)
            {
                Foreground.Add(new ForegroundObject(Width, _rng));
                _foregroundCooldown = _rng.Int(60, 240);
            }
            else _foregroundCooldown = Math.Max(0, _foregroundCooldown - 1);

            for (int i = Foreground.Count - 1; i >= 0; i--)
            {
                Foreground[i].Update();
                if (Foreground[i].Expired(Height)) Foreground.RemoveAt(i);
            }

            if (Transition.Active && (_clock.NowMs - Transition.StartMs) >= Transition.DurationMs)
            {
                Transition.Active = false;
                CompleteTransition();
            }
        }

        private void MaybeSpawnPlanet(bool allow)
        {
            if (!allow) return;
            if (_spawnCooldown > 0) { _spawnCooldown = Math.Max(0, _spawnCooldown - 1); return; }
            if (_planetPool.Length == 0 || _planetSpawned) return;
            string key = _planetPool[_rng.Int(0, _planetPool.Length - 1)];
            var planet = new PlanetObject(key, Width, _rng, 0.6, 1.6);
            foreach (var e in Planets)
                if (!e.IsExiting && planet.Rect.Colliderect(e.Rect)) return;
            Planets.Add(planet);
            _planetSpawned = true;
            _spawnCooldown = _rng.Int(500, 1000);
        }
    }
}
