using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>game/enemies/ai.py – taktische Entscheidungsschicht mit Reaktionstimer.</summary>
    public sealed class EnemyBrain
    {
        private static readonly Dictionary<string, double> RoleOffsets = new Dictionary<string, double> { { "attacker", 0.0 }, { "support", 0.18 }, { "flanker_left", -0.26 }, { "flanker_right", 0.26 } };
        private static readonly Dictionary<string, double> RoleY = new Dictionary<string, double> { { "attacker", 0.34 }, { "support", 0.18 }, { "flanker_left", 0.27 }, { "flanker_right", 0.27 } };

        private readonly EnemyShip _owner;
        private readonly ISimRandom _rng;
        public string Role;
        public double ReactionTimer, TargetX, TargetY, Jitter, DodgeTime, DodgeVelocity, DodgeLockout;
        public int StrafeSign;

        public EnemyBrain(EnemyShip owner, string role, ISimRandom rng)
        {
            _owner = owner; Role = role; _rng = rng;
            ReactionTimer = rng.Uniform(owner.Archetype.ReactionMin, owner.Archetype.ReactionMax);
            TargetX = owner.CenterX;
            TargetY = Math.Max(owner.Height, owner.WindowHeight * (RoleY.TryGetValue(role, out var ry) ? ry : 0.28));
            Jitter = rng.Uniform(-55.0, 55.0);
            DodgeLockout = rng.Uniform(0.35, 0.8);
            StrafeSign = rng.Choice(-1, 1);
        }

        private bool ProjectileThreat(PlayerProjectile p)
        {
            var e = _owner;
            double verticalDistance = e.Hitbox.Bottom - p.Rect.Top;
            if (verticalDistance >= 0) return false;
            double speedPerSecond = Math.Max(60.0, p.Speed * 60.0);
            double timeToEnemy = Math.Abs(verticalDistance) / speedPerSecond;
            if (timeToEnemy > 0.72) return false;
            double margin = 22 + Math.Abs(e.Vx) * Math.Min(0.20, timeToEnemy);
            return (e.Hitbox.Left - margin) <= p.Rect.CenterX && p.Rect.CenterX <= (e.Hitbox.Right + margin);
        }

        private void ChooseDodge(IReadOnlyList<PlayerProjectile> projectiles, IReadOnlyList<EnemyShip> nearby)
        {
            var e = _owner;
            if (DodgeLockout > 0) return;
            bool threat = false;
            foreach (var p in projectiles) if (ProjectileThreat(p)) { threat = true; break; }
            if (!threat) return;
            if (_rng.NextDouble() > e.Archetype.DodgeChance) { DodgeLockout = _rng.Uniform(0.20, 0.55); return; }

            double leftSpace = e.X, rightSpace = e.WindowWidth - (e.X + e.Width);
            int direction = leftSpace > rightSpace ? -1 : 1;
            foreach (var other in nearby)
            {
                if (ReferenceEquals(other, e) || !other.Alive) continue;
                if (Math.Abs(other.CenterY - e.CenterY) < e.Height * 1.5)
                {
                    if (0 < other.CenterX - e.CenterX && other.CenterX - e.CenterX < e.Width * 2.0) direction = -1;
                    else if (0 < e.CenterX - other.CenterX && e.CenterX - other.CenterX < e.Width * 2.0) direction = 1;
                }
            }
            if (_rng.NextDouble() < 0.25) direction *= -1;
            DodgeVelocity = direction * e.MaxSpeed * _rng.Uniform(1.05, 1.35);
            DodgeTime = _rng.Uniform(0.20, 0.46);
            DodgeLockout = _rng.Uniform(0.65, 1.35);
        }

        public void Update(double dt, PlayerShip player, IReadOnlyList<PlayerProjectile> playerProjectiles, IReadOnlyList<EnemyShip> nearby, double difficultyScale,
            out double targetX, out double targetY, out double dodgeVelocity)
        {
            var e = _owner;
            ReactionTimer -= dt;
            DodgeLockout = Math.Max(0.0, DodgeLockout - dt);
            if (DodgeTime > 0) DodgeTime -= dt;
            else DodgeVelocity *= Math.Max(0.0, 1.0 - 7.0 * dt);

            if (ReactionTimer <= 0)
            {
                double playerCenterX = player.Hitbox.CenterX;
                double roleOffset = (RoleOffsets.TryGetValue(Role, out var ro) ? ro : 0.0) * e.WindowWidth;
                double lead = e.EstimatedPlayerVx * (0.10 + e.Archetype.Accuracy * 0.18);
                Jitter = _rng.Uniform(-1.0, 1.0) * (80.0 * (1.0 - e.Archetype.Accuracy));
                TargetX = playerCenterX + roleOffset + lead + Jitter;
                TargetY = e.WindowHeight * (RoleY.TryGetValue(Role, out var ry) ? ry : 0.28);

                if (Role == "attacker" && _rng.NextDouble() < 0.17) TargetY = e.WindowHeight * _rng.Uniform(0.38, 0.50);
                else if (Role == "support") TargetY = e.WindowHeight * _rng.Uniform(0.13, 0.23);

                ChooseDodge(playerProjectiles, nearby);

                double reactionFactor = Math.Max(0.72, 1.0 / Math.Max(1.0, difficultyScale * 0.08 + 1.0));
                ReactionTimer = _rng.Uniform(e.Archetype.ReactionMin, e.Archetype.ReactionMax) * reactionFactor;
            }
            targetX = TargetX; targetY = TargetY; dodgeVelocity = DodgeVelocity;
        }
    }

    /// <summary>game/enemies/movement.py – beschleunigungsbegrenztes Steering.</summary>
    public sealed class EnemyMovement
    {
        private readonly EnemyShip _owner;
        public EnemyMovement(EnemyShip owner) { _owner = owner; }

        private static double Approach(double current, double target, double maxDelta)
            => current < target ? Math.Min(current + maxDelta, target) : Math.Max(current - maxDelta, target);

        public void Update(double dt, double targetX, double targetY, double dodgeVelocity = 0.0)
        {
            var e = _owner;
            double dx = targetX - e.CenterX, dy = targetY - e.CenterY;
            double desiredVx = PyMath.Clamp(dx * 2.2, -e.MaxSpeed, e.MaxSpeed) + dodgeVelocity;
            desiredVx = PyMath.Clamp(desiredVx, -e.MaxSpeed * 1.35, e.MaxSpeed * 1.35);
            double desiredVy = PyMath.Clamp(dy * 1.4, -e.MaxSpeed * 0.55, e.MaxSpeed * 0.55);

            double maxChange = e.Acceleration * dt;
            e.Vx = Approach(e.Vx, desiredVx, maxChange);
            e.Vy = Approach(e.Vy, desiredVy, maxChange * 0.72);

            double length = Math.Sqrt(e.Vx * e.Vx + e.Vy * e.Vy);
            double maxTotal = e.MaxSpeed * 1.12;
            if (length > maxTotal) { double s = maxTotal / length; e.Vx *= s; e.Vy *= s; }

            e.X += e.Vx * dt; e.Y += e.Vy * dt;
            e.X = Math.Max(0.0, Math.Min(e.X, e.WindowWidth - e.Width));
            double maxY = Math.Max(80.0, e.WindowHeight * 0.58 - e.Height);
            e.Y = Math.Max(-e.Height * 0.15, Math.Min(e.Y, maxY));
            e.UpdateHitbox();
        }
    }

    /// <summary>game/enemies/weapons.py – Salven, gezielte Laser, taktische Torpedos.</summary>
    public sealed class EnemyWeaponSystem
    {
        private readonly EnemyShip _owner;
        private readonly ISimRandom _rng;
        public double LaserTimer, TorpedoTimer, BurstTimer;
        public int BurstRemaining;

        public EnemyWeaponSystem(EnemyShip owner, ISimRandom rng)
        {
            _owner = owner; _rng = rng;
            LaserTimer = rng.Uniform(0.35, 1.2);
            TorpedoTimer = rng.Uniform(owner.Archetype.TorpedoCooldownMin, owner.Archetype.TorpedoCooldownMax);
        }

        private void AimPoint(PlayerShip player, double diff, out double tx, out double ty)
        {
            var e = _owner;
            double distanceY = Math.Max(1.0, player.Hitbox.CenterY - e.Hitbox.CenterY);
            double flightTime = Math.Min(0.75, distanceY / 470.0);
            double accuracy = Math.Min(0.97, e.Archetype.Accuracy + 0.015 * diff);
            double prediction = e.EstimatedPlayerVx * flightTime * accuracy;
            double spread = (1.0 - accuracy) * 160.0;
            tx = player.Hitbox.CenterX + prediction + _rng.Uniform(-spread, spread);
            ty = player.Hitbox.CenterY + _rng.Uniform(-10.0, 18.0);
        }

        private EnemyProjectile FireLaser(PlayerShip player, double diff)
        {
            AimPoint(player, diff, out var tx, out var ty);
            double muzzleX = _owner.Hitbox.CenterX + _rng.Choice(-1, 1) * _owner.Width * 0.12;
            double muzzleY = _owner.Hitbox.Bottom - 4;
            return new EnemyLaser(muzzleX, muzzleY, tx, ty, _owner.Archetype.LaserDamage, 470.0 + Math.Min(90.0, diff * 8.0));
        }

        private bool CanUseTorpedo(PlayerShip player)
        {
            var e = _owner;
            if (player.Hitbox.CenterY <= e.Hitbox.CenterY) return false;
            double horizontalError = Math.Abs(player.Hitbox.CenterX - e.Hitbox.CenterX);
            double alignmentLimit = Math.Max(55.0, e.Width * 0.72);
            return horizontalError <= alignmentLimit;
        }

        public List<EnemyProjectile> Update(double dt, PlayerShip player, double diff)
        {
            var spawned = new List<EnemyProjectile>();
            var e = _owner;
            LaserTimer -= dt; TorpedoTimer -= dt; BurstTimer -= dt;
            if (player.Hitbox.CenterY <= e.Hitbox.CenterY) return spawned;

            if (BurstRemaining > 0 && BurstTimer <= 0)
            {
                spawned.Add(FireLaser(player, diff));
                BurstRemaining--;
                BurstTimer = _rng.Uniform(0.08, 0.16);
            }
            if (BurstRemaining <= 0 && LaserTimer <= 0)
            {
                BurstRemaining = _rng.Int(e.Archetype.BurstMin, e.Archetype.BurstMax);
                BurstTimer = 0.0;
                double fireRateFactor = Math.Max(0.58, 1.0 - diff * 0.035);
                LaserTimer = _rng.Uniform(e.Archetype.LaserCooldownMin, e.Archetype.LaserCooldownMax) * fireRateFactor;
            }
            if (TorpedoTimer <= 0 && CanUseTorpedo(player))
            {
                double tactical = Math.Min(0.92, e.Archetype.TorpedoChance + diff * 0.018);
                if (_rng.NextDouble() < tactical)
                {
                    AimPoint(player, diff, out var tx, out var ty);
                    spawned.Add(new EnemyTorpedo(e.Hitbox.CenterX, e.Hitbox.Bottom, tx, ty, e.Archetype.TorpedoDamage, 285.0 + Math.Min(55.0, diff * 5.0)));
                }
                TorpedoTimer = _rng.Uniform(e.Archetype.TorpedoCooldownMin, e.Archetype.TorpedoCooldownMax) / Math.Max(1.0, 1.0 + diff * 0.03);
            }
            return spawned;
        }
    }

    /// <summary>game/enemies/base.py – ein KI-Schiff (Archetyp + Brain + Movement + Weapons).</summary>
    public sealed class EnemyShip
    {
        public readonly EnemyArchetype Archetype;
        public readonly string ShipKey;      // Gegnerschiff (z. B. "tiefighter")
        public readonly int WindowWidth, WindowHeight;
        public double X, Y, Vx, Vy;
        public readonly int Width, Height;
        public int MaxHp, Hp;
        public double MaxSpeed, Acceleration;
        public bool Alive = true;
        public double DamageFlashTimer;
        public double? PreviousPlayerX;
        public double EstimatedPlayerVx;
        public readonly double VisualScale;
        public RectI Hitbox;
        private readonly int _hitOffX, _hitOffY;
        public readonly EnemyBrain Brain;
        public readonly EnemyMovement Movement;
        public readonly EnemyWeaponSystem Weapons;
        private readonly ISimRandom _rng;

        public double CenterX => X + Width * 0.5;
        public double CenterY => Y + Height * 0.5;

        public EnemyShip(string playerClassName, string enemyShipKey, EnemyArchetype archetype, int windowWidth, int windowHeight, double spawnX, double spawnY, string role, ISimRandom rng)
        {
            _rng = rng; Archetype = archetype; ShipKey = enemyShipKey; WindowWidth = windowWidth; WindowHeight = windowHeight;
            var m = AssetMetrics.Enemies[playerClassName + "/" + archetype.Key];
            Width = m.Width; Height = m.Height; _hitOffX = m.HitX; _hitOffY = m.HitY;
            VisualScale = 96.0 / Math.Max(1, SpriteBaseHeight(enemyShipKey)) * archetype.VisualScaleMultiplier;
            X = spawnX; Y = spawnY;
            MaxHp = archetype.MaxHp; Hp = MaxHp; MaxSpeed = archetype.MaxSpeed; Acceleration = archetype.Acceleration;
            Hitbox = new RectI(PyMath.Round(X) + _hitOffX, PyMath.Round(Y) + _hitOffY, m.HitW, m.HitH);
            Movement = new EnemyMovement(this);
            Brain = new EnemyBrain(this, role, rng);
            Weapons = new EnemyWeaponSystem(this, rng);
        }

        private static int SpriteBaseHeight(string key) => key == "milleniumfalcon" ? 1484 : 1254;

        public void UpdateHitbox() { Hitbox.X = PyMath.Round(X + _hitOffX); Hitbox.Y = PyMath.Round(Y + _hitOffY); }

        public List<EnemyProjectile> Update(double dt, PlayerShip player, IReadOnlyList<PlayerProjectile> playerProjectiles, IReadOnlyList<EnemyShip> nearby, double difficultyScale)
        {
            if (!Alive) return new List<EnemyProjectile>();
            if (PreviousPlayerX.HasValue && dt > 0)
            {
                double instantaneous = (player.Hitbox.CenterX - PreviousPlayerX.Value) / dt;
                EstimatedPlayerVx = EstimatedPlayerVx * 0.78 + instantaneous * 0.22;
            }
            PreviousPlayerX = player.Hitbox.CenterX;
            Brain.Update(dt, player, playerProjectiles, nearby, difficultyScale, out var tx, out var ty, out var dodge);
            Movement.Update(dt, tx, ty, dodge);
            DamageFlashTimer = Math.Max(0.0, DamageFlashTimer - dt);
            return Weapons.Update(dt, player, difficultyScale);
        }

        /// <summary>Gibt true zurück, wenn zerstört. Rüstung wird über das zentrale CombatSystem verrechnet.</summary>
        public bool TakeDamage(int amount)
        {
            int effective = CombatSystem.EffectiveDamage(amount, Archetype.ArmorResistance);
            Hp -= effective;
            DamageFlashTimer = 0.11;
            if (Hp <= 0) { Hp = 0; Alive = false; }
            return !Alive;
        }

        public int ScoreValue() => Archetype.BaseScore + _rng.Int(Archetype.BonusMin, Archetype.BonusMax);
    }
}
