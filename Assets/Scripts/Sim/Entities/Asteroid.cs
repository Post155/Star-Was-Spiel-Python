using System;

namespace StarWars.Sim
{
    /// <summary>Asteroid (game/entities/asteroid.py). Zeitbasis: pro Tick (60 Hz) wie die Frame-Logik im Original.</summary>
    public sealed class Asteroid
    {
        public double X, Y, Vx, Vy, Speed;
        public int Width, Height, Frame, FrameCounter;
        public double Scale;
        public readonly int FrameDelay = 5;
        public string Id;

        public Asteroid(int windowWidth, int windowHeight, ISimRandom rng, double sizeMultiplier = 1.0, double speedMultiplier = 1.0)
        {
            Scale = rng.Choice(0.25, 0.5, 0.75, 1.0) * sizeMultiplier;
            Scale = Math.Max(0.18, Math.Min(1.25, Scale));
            double s = Scale * (windowHeight / 600.0);
            Width = PyMath.ScaleDim(AssetMetrics.AsteroidFrameSize, s);
            Height = PyMath.ScaleDim(AssetMetrics.AsteroidFrameSize, s);
            X = rng.Int(0, Math.Max(0, windowWidth - Width));
            Y = -Height;
            Speed = rng.Int(GameConstants.AsteroidSpeedMin, GameConstants.AsteroidSpeedMax) * speedMultiplier;
            Vx = 0.0; Vy = Speed;
        }

        public void Update()
        {
            X += Vx; Y += Vy;
            FrameCounter++;
            if (FrameCounter >= FrameDelay)
            {
                FrameCounter = 0;
                Frame = (Frame + 1) % AssetMetrics.AsteroidFrameCount;
            }
        }

        /// <summary>Kollisionsrechteck: zentrale 70 % des Sprites.</summary>
        public RectI GetRect() => RectI.FromFloats(X + Width * 0.15, Y + Height * 0.15, Width * 0.7, Height * 0.7);

        public int GetPoints() => Scale <= 0.5 ? 100 : (Scale <= 0.75 ? 75 : 50);
    }

    /// <summary>Explosions-Effekt (game/entities/explosion.py): 20 Frames Lebensdauer.</summary>
    public sealed class Explosion
    {
        public double X, Y, Scale;
        public int Timer = 20;
        public int Width, Height;
        public Explosion(double x, double y, double scale)
        {
            X = x; Y = y; Scale = scale;
            Width = PyMath.ScaleDim(AssetMetrics.ExplosionBaseWidth, scale * 0.5);
            Height = PyMath.ScaleDim(AssetMetrics.ExplosionBaseHeight, scale * 0.5);
        }
        public RectI Rect => RectI.FromCenter(X, Y, Width, Height);
        /// <summary>true, sobald abgelaufen.</summary>
        public bool Update() { Timer--; return Timer <= 0; }
    }
}
