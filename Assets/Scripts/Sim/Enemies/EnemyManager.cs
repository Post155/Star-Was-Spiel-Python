using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    public struct EnemyUpdateResult
    {
        public int ScoreDelta;
        public bool PlayerDead;
        public string WarningText;
        public int EnemiesDestroyed;
    }

    /// <summary>game/enemies/manager.py – Spawn, Balancing, Freischaltung, Kollisionen und Lebenszyklus der KI-Gegner.</summary>
    public sealed class EnemyManager
    {
        public int Width, Height;
        public PlayerShip Player;
        public string Difficulty;
        public readonly List<EnemyShip> Enemies = new List<EnemyShip>();
        public readonly List<EnemyProjectile> Projectiles = new List<EnemyProjectile>();
        public readonly List<Explosion> Explosions = new List<Explosion>();
        public double SpawnTimer = 1.0;
        private int _roleCursor;
        public string WarningText;
        public int WarningTimerMs;
        public int? WarningPendingTier;
        public readonly HashSet<int> WarnedTiers = new HashSet<int>();
        private readonly ISimRandom _rng;
        public event Action<EnemyShip, int> EnemyDestroyed;

        public EnemyManager(int width, int height, PlayerShip player, string difficulty, ISimRandom rng)
        {
            Width = width; Height = height; Player = player; _rng = rng;
            Difficulty = Difficulties.IsValid(difficulty) ? difficulty : GameConstants.DefaultDifficulty;
        }

        public void SetPlayer(PlayerShip player, bool clearExisting = true)
        {
            Player = player;
            if (clearExisting) { Enemies.Clear(); Projectiles.Clear(); SpawnTimer = 1.0; }
        }

        private DifficultyProfile Profile => Difficulties.Get(Difficulty);

        public static double SystemBonus(int systemIndex) => Difficulties.SystemBonus(systemIndex);

        public double DifficultyScale(int score, int systemIndex)
        {
            double systemBonus = SystemBonus(systemIndex);
            double progress = 0.0;
            if (score > GameConstants.EnemyUnlockStandardPoints)
                progress = Math.Min(GameConstants.SystemProgressMaxBonus,
                    (score - GameConstants.EnemyUnlockStandardPoints) / 5000.0 * GameConstants.SystemProgressMaxBonus);
            return Math.Max(0.75, 1.0 + systemBonus + progress);
        }

        public static int UnlockedTier(int score)
        {
            if (score >= GameConstants.EnemyUnlockElitePoints) return 3;
            if (score >= GameConstants.EnemyUnlockHeavyPoints) return 2;
            if (score >= GameConstants.EnemyUnlockStandardPoints) return 1;
            return 0;
        }

        public static string TierWarning(int tier)
        {
            switch (tier)
            {
                case 1: return "Achtung! Feindliche Schiffe wurden entdeckt.";
                case 2: return "Warnung: Schwere Feinde im Anflug!";
                case 3: return "WARNUNG: Elite-Einheit im Anflug!";
                default: return null;
            }
        }

        private void CheckUnlockWarning(int score)
        {
            int tier = UnlockedTier(score);
            if (WarningPendingTier.HasValue) return;
            for (int newTier = 1; newTier <= 3; newTier++)
            {
                if (tier >= newTier && !WarnedTiers.Contains(newTier))
                {
                    WarningPendingTier = newTier;
                    WarningText = TierWarning(newTier);
                    WarningTimerMs = GameConstants.EnemyWarningDurationMs;
                    return;
                }
            }
        }

        private bool WarningActive(double dt)
        {
            if (!WarningPendingTier.HasValue) return false;
            WarningTimerMs -= (int)(dt * 1000);
            if (WarningTimerMs <= 0)
            {
                WarnedTiers.Add(WarningPendingTier.Value);
                WarningPendingTier = null;
                WarningText = null;
                return false;
            }
            return true;
        }

        public int MaxEnemies(int score, int systemIndex)
        {
            double scale = DifficultyScale(score, systemIndex);
            int baseCount = 1 + Math.Min(5, (int)(Math.Max(0, score - 1000) / 1800));
            int cap = PyMath.Round(baseCount * Profile.EnemyMax * (1.0 + (scale - 1.0) * 0.45));
            return Math.Max(1, Math.Min(8, cap));
        }

        /// <summary>Intervall ohne den Zufallsfaktor 0.90–1.12 (für deterministische Tests).</summary>
        public double SpawnIntervalBase(int score, int systemIndex)
        {
            double scale = DifficultyScale(score, systemIndex);
            double pressure = 1.0 + Math.Max(0.0, scale - 1.0) * 0.45;
            double interval = 2.60 * Profile.EnemySpawn / pressure;
            if (score < GameConstants.EnemyUnlockHeavyPoints) interval += 0.55;
            if (score < GameConstants.EnemyUnlockElitePoints) interval += 0.25;
            return Math.Max(1.15, interval);
        }

        private double SpawnInterval(int score, int systemIndex) => SpawnIntervalBase(score, systemIndex) * _rng.Uniform(0.90, 1.12);

        private EnemyArchetype ChooseArchetype(int score, int systemIndex)
        {
            int tier = UnlockedTier(score);
            double scale = DifficultyScale(score, systemIndex);
            var a = EnemyArchetypes.All;
            if (tier <= 0) return null;
            if (tier == 1) return _rng.NextDouble() < 0.30 ? a["fast"] : a["standard"];
            if (tier == 2)
            {
                double roll = _rng.NextDouble();
                if (roll < 0.14 + Math.Max(0, scale - 1.0) * 0.10) return a["fast"];
                if (roll < 0.36) return a["heavy"];
                return a["standard"];
            }
            double r = _rng.NextDouble();
            if (r < 0.10 + Math.Max(0, scale - 1.0) * 0.08) return a["elite"];
            if (r < 0.34) return a["heavy"];
            if (r < 0.56) return a["fast"];
            return a["standard"];
        }

        /// <summary>Wendet Schwierigkeitsgrad und Systemfortschritt auf eine Kopie des Archetyps an.</summary>
        public EnemyArchetype BalancedArchetype(EnemyArchetype archetype, int score, int systemIndex)
        {
            var p = Profile;
            double scale = DifficultyScale(score, systemIndex);
            double systemFactor = 1.0 + Math.Max(0.0, scale - 1.0);
            double hpFactor = p.EnemyHp * (1.0 + (systemFactor - 1.0) * 0.55);
            double speedFactor = p.EnemySpeed * (1.0 + (systemFactor - 1.0) * 0.65);
            double accuracy = Math.Min(0.96, archetype.Accuracy * p.EnemyAccuracy + Math.Max(0.0, scale - 1.0) * 0.025);
            double aggression = p.EnemyAggression * (1.0 + (systemFactor - 1.0) * 0.45);
            double reactionFactor = Math.Max(0.72, Math.Min(1.20, 1.0 / aggression));

            var c = archetype.Clone();
            c.ReactionMin = Math.Max(0.08, archetype.ReactionMin * reactionFactor);
            c.ReactionMax = Math.Max(0.12, archetype.ReactionMax * reactionFactor);
            c.DodgeChance = Math.Min(0.82, archetype.DodgeChance * (0.82 + 0.18 * aggression));
            c.TorpedoChance = Math.Min(0.65, archetype.TorpedoChance * (0.85 + 0.15 * aggression));
            c.MaxHp = Math.Max(1, PyMath.Round(archetype.MaxHp * hpFactor));
            c.MaxSpeed = archetype.MaxSpeed * speedFactor;
            c.Acceleration = archetype.Acceleration * Math.Min(1.22, 0.90 + aggression * 0.10);
            c.Accuracy = accuracy;
            return c;
        }

        private string ChooseRole()
        {
            if (Enemies.Count == 0) return "attacker";
            string[] roles = { "attacker", "flanker_left", "flanker_right", "support" };
            string role = roles[_roleCursor % roles.Length];
            _roleCursor++;
            return role;
        }

        private void SpawnPosition(double spriteWidth, double spriteHeight, out double x, out double y)
        {
            const int margin = 12;
            double maxX = Math.Max(margin, Width - spriteWidth - margin);
            for (int i = 0; i < 18; i++)
            {
                x = _rng.Uniform(margin, maxX);
                y = _rng.Uniform(-spriteHeight * 0.10, Math.Max(18.0, Height * 0.10));
                double left = x - 24, right = x + spriteWidth + 24;
                bool blocked = false;
                foreach (var e in Enemies)
                    if (e.Y <= Height * 0.22 && left < e.X + e.Width + 24 && right > e.X - 24) { blocked = true; break; }
                if (!blocked) return;
            }
            int slots = Math.Max(1, Width / Math.Max(90, (int)(spriteWidth + 35)));
            int slot = Enemies.Count % slots;
            x = Math.Min(maxX, margin + slot * ((Width - margin * 2) / (double)slots));
            y = -spriteHeight * 0.10;
        }

        private static int BaseImageWidth(string key) => key == "milleniumfalcon" ? 1060 : 1254;
        private static int BaseImageHeight(string key) => key == "milleniumfalcon" ? 1484 : 1254;

        private void SpawnEnemy(int score, int systemIndex)
        {
            var baseArch = ChooseArchetype(score, systemIndex);
            if (baseArch == null) return;
            var arch = BalancedArchetype(baseArch, score, systemIndex);
            string enemyKey = Player.Info.OpposingKey;
            // Original-Verhalten: approx_width nutzt die UNskalierte Bildgröße (ship_scale = 1) – dadurch
            // landen Gegner praktisch immer am linken Rand (Spawnposition x = 12). Bewusst 1:1 übernommen.
            double approxW = Math.Max(24, BaseImageWidth(enemyKey) * 1.0 * arch.VisualScaleMultiplier);
            double approxH = Math.Max(24, BaseImageHeight(enemyKey) * 1.0 * arch.VisualScaleMultiplier);
            SpawnPosition(approxW, approxH, out var sx, out var sy);
            Enemies.Add(new EnemyShip(Player.Info.ClassName, enemyKey, arch, Width, Height, sx, sy, ChooseRole(), _rng));
        }

        private static int PlayerProjectileDamage(PlayerProjectile p) => p.IsTorpedo ? 4 : 1;

        private int DestroyEnemy(EnemyShip enemy, bool awardScore)
        {
            Enemies.Remove(enemy);
            double explosionScale = Math.Max(0.55, Math.Min(1.20, enemy.VisualScale * 2.3));
            Explosions.Add(new Explosion(enemy.CenterX, enemy.CenterY, explosionScale));
            int score = awardScore ? enemy.ScoreValue() : 0;
            if (awardScore) EnemyDestroyed?.Invoke(enemy, score);
            return score;
        }

        private int HandlePlayerShots(List<PlayerProjectile> lasers, List<PlayerProjectile> torpedoes, ref int destroyed)
        {
            int scoreDelta = 0;
            foreach (var list in new[] { lasers, torpedoes })
            {
                foreach (var projectile in list.ToArray())
                {
                    EnemyShip hit = null;
                    foreach (var e in Enemies) if (e.Alive && e.Hitbox.Colliderect(projectile.Rect)) { hit = e; break; }
                    if (hit == null) continue;
                    list.Remove(projectile);
                    if (hit.TakeDamage(PlayerProjectileDamage(projectile))) { scoreDelta += DestroyEnemy(hit, true); destroyed++; }
                }
            }
            return scoreDelta;
        }

        private bool HandleEnemyProjectiles()
        {
            bool dead = false;
            foreach (var p in Projectiles.ToArray())
            {
                if (!p.Alive) { Projectiles.Remove(p); continue; }
                if (p.Rect.Colliderect(Player.Hitbox))
                {
                    dead = Player.TakeDamage(Math.Max(1, p.Damage)) || dead;
                    p.Alive = false;
                    Projectiles.Remove(p);
                }
            }
            return dead;
        }

        private bool HandleShipCollisions()
        {
            bool dead = false;
            foreach (var e in Enemies.ToArray())
            {
                if (e.Alive && e.Hitbox.Colliderect(Player.Hitbox))
                {
                    dead = Player.TakeDamage(1) || dead;
                    e.Alive = false;
                    DestroyEnemy(e, false);
                }
            }
            return dead;
        }

        public EnemyUpdateResult Update(double dt, int score, int systemDifficulty, List<PlayerProjectile> lasers, List<PlayerProjectile> torpedoes)
        {
            var result = new EnemyUpdateResult();
            CheckUnlockWarning(score);
            bool warningWasActive = WarningActive(dt);

            if (!warningWasActive)
            {
                SpawnTimer -= dt;
                int tier = UnlockedTier(score);
                if (tier > 0 && !WarningPendingTier.HasValue && SpawnTimer <= 0 && Enemies.Count < MaxEnemies(score, systemDifficulty))
                {
                    SpawnEnemy(score, systemDifficulty);
                    SpawnTimer = SpawnInterval(score, systemDifficulty);
                }
            }

            double diffScale = DifficultyScale(score, systemDifficulty);
            var playerProjectiles = new List<PlayerProjectile>(lasers.Count + torpedoes.Count);
            playerProjectiles.AddRange(lasers); playerProjectiles.AddRange(torpedoes);

            foreach (var enemy in Enemies.ToArray())
                if (enemy.Alive) Projectiles.AddRange(enemy.Update(dt, Player, playerProjectiles, Enemies, diffScale));

            foreach (var p in Projectiles.ToArray())
            {
                p.Update(dt, Width, Height);
                if (!p.Alive) Projectiles.Remove(p);
            }

            int destroyed = 0;
            result.ScoreDelta += HandlePlayerShots(lasers, torpedoes, ref destroyed);
            result.EnemiesDestroyed = destroyed;
            result.PlayerDead = HandleEnemyProjectiles() || result.PlayerDead;
            result.PlayerDead = HandleShipCollisions() || result.PlayerDead;

            foreach (var ex in Explosions.ToArray()) if (ex.Update()) Explosions.Remove(ex);

            result.WarningText = WarningText;
            return result;
        }
    }
}
