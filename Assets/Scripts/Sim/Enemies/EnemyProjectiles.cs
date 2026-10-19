using System;

namespace StarWars.Sim
{
    /// <summary>game/enemies/projectiles.py – Geschosse der KI (Geschwindigkeit in Pixeln/Sekunde).</summary>
    public abstract class EnemyProjectile
    {
        public double X, Y, Vx, Vy;
        public int Damage;
        public bool Alive = true;
        public RectI Rect;
        public abstract bool IsTorpedo { get; }
        protected int RectW, RectH;

        protected EnemyProjectile(double x, double y, double tx, double ty, double speed, int damage)
        {
            X = x; Y = y; Damage = damage;
            double dx = tx - X, dy = ty - Y;
            double len = Math.Max(1.0, Math.Sqrt(dx * dx + dy * dy));
            Vx = dx / len * speed; Vy = dy / len * speed;
        }

        protected void SyncRect() { Rect = RectI.FromCenter(PyMath.Round(X), PyMath.Round(Y), RectW, RectH); }

        public void Update(double dt, int width, int height)
        {
            X += Vx * dt; Y += Vy * dt;
            SyncRect();
            const int margin = 100;
            if (Rect.Right < -margin || Rect.Left > width + margin || Rect.Bottom < -margin || Rect.Top > height + margin)
                Alive = false;
        }
    }

    public sealed class EnemyLaser : EnemyProjectile
    {
        public EnemyLaser(double x, double y, double tx, double ty, int damage = 1, double speed = 470.0) : base(x, y, tx, ty, speed, damage)
        { RectW = 5; RectH = 22; SyncRect(); }
        public override bool IsTorpedo => false;
    }

    public sealed class EnemyTorpedo : EnemyProjectile
    {
        public EnemyTorpedo(double x, double y, double tx, double ty, int damage = 2, double speed = 285.0) : base(x, y, tx, ty, speed, damage)
        {
            RectW = PyMath.ScaleDim(AssetMetrics.TorpedoBaseWidth, 0.42);
            RectH = PyMath.ScaleDim(AssetMetrics.TorpedoBaseHeight, 0.42);
            SyncRect();
        }
        public override bool IsTorpedo => true;
    }
}
