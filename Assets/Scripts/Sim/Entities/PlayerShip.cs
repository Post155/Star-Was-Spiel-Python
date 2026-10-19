using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>
    /// Spielerschiff (game/entities/player.py + ships.py). Position/Hitbox ganzzahlig wie in Pygame.
    /// Die Alpha-Hitbox stammt aus AssetMetrics (am Original gemessen).
    /// </summary>
    public sealed class PlayerShip
    {
        public readonly ShipInfo Info;
        public int X, Y, Width, Height, Speed;
        public int Lives = GameConstants.PlayerLives;
        public double InvulnerableUntilMs;
        public bool ShowHitbox;
        private readonly int _hitOffX, _hitOffY, _hitW, _hitH;
        private readonly SimClock _clock;
        public RectI Hitbox;

        public PlayerShip(ShipInfo info, int windowWidth, int windowHeight, SimClock clock)
        {
            Info = info; _clock = clock;
            var m = AssetMetrics.Ships[info.Key];
            Width = m.Width; Height = m.Height;
            _hitOffX = m.HitX; _hitOffY = m.HitY; _hitW = m.HitW; _hitH = m.HitH;
            Speed = info.Speed;
            X = windowWidth / 2 - Width / 2;
            Y = windowHeight - Height - 20;
            Hitbox = new RectI(0, 0, _hitW, _hitH);
            UpdateHitbox();
        }

        public void UpdateHitbox() { Hitbox.X = X + _hitOffX; Hitbox.Y = Y + _hitOffY; }

        public bool IsInvulnerable => _clock.NowMs < InvulnerableUntilMs;

        /// <summary>Gibt true zurück, wenn das Schiff dadurch zerstört wurde. Ignoriert Schaden während der Unverwundbarkeit.</summary>
        public bool TakeDamage(int amount = 1)
        {
            if (_clock.NowMs < InvulnerableUntilMs) return false;
            if (amount < 1) amount = 1;
            Lives = System.Math.Max(0, Lives - amount);
            InvulnerableUntilMs = _clock.NowMs + GameConstants.InvulnerableDurationMs;
            return Lives <= 0;
        }

        public void Resize(int windowWidth, int windowHeight)
        {
            Y = windowHeight - Height - 20;
            X = System.Math.Max(0, System.Math.Min(X, windowWidth - Width));
            UpdateHitbox();
        }

        public void MoveLeft() { X -= Speed; if (X < 0) X = 0; UpdateHitbox(); }
        public void MoveRight(int windowWidth) { X += Speed; if (X > windowWidth - Width) X = windowWidth - Width; UpdateHitbox(); }

        /// <summary>Sichtbarkeit beim Blinken (Original: (ticks // 200) % 2 == 0 sichtbar).</summary>
        public bool BlinkVisible()
        {
            if (!IsInvulnerable) return true;
            return ((long)_clock.NowMs / GameConstants.InvulnerableBlinkMs) % 2 == 0;
        }

        public List<PlayerProjectile> Shoot()
        {
            var l = new List<PlayerProjectile>(2);
            for (int i = 0; i < Info.LaserFx.Length; i++)
                l.Add(new Laser(X + Width * Info.LaserFx[i], Y + Height * Info.LaserFy[i]));
            return l;
        }

        /// <summary>Torpedo oder null, wenn das Schiff keinen besitzt (Falcon, Battle Droid).</summary>
        public PlayerProjectile FireTorpedo()
        {
            if (!Info.HasTorpedo) return null;
            if (Info.TorpedoFromHitbox) return new Torpedo(Hitbox.CenterX, Y);
            return new Torpedo(X + Width * 0.47, Y + Height * 0.12);
        }
    }
}
