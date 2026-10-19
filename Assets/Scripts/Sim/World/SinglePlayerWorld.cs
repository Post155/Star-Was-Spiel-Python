using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>Eingabe eines Spielers für einen Tick. Schüsse sind Ereignisse (KEYDOWN), Bewegung ist Zustand (get_pressed).</summary>
    public struct PlayerInput
    {
        public bool Left, Right, Laser, Torpedo;
    }

    /// <summary>
    /// Komplette Einzelspieler-Simulation (run_game_session aus StarWarsGame.py). Läuft mit festem 60-Hz-Takt;
    /// dieselbe Klasse bildet jede Spielwelt des Punktekampfs (lokal und LAN) ab – dadurch bleiben die Welten
    /// garantiert voneinander getrennt (jede Instanz besitzt eigene Objekte, eigene Uhr und eigenen Zufall).
    /// </summary>
    public sealed class SinglePlayerWorld
    {
        public readonly int Width, Height;
        public readonly SimClock Clock = new SimClock();
        public readonly ISimRandom Rng;
        public PlayerShip Player { get; private set; }
        public readonly EnemyManager Enemies;
        public readonly BackgroundDirector Background;
        public readonly List<PlayerProjectile> Lasers = new List<PlayerProjectile>();
        public readonly List<PlayerProjectile> Torpedoes = new List<PlayerProjectile>();
        public readonly List<Asteroid> Asteroids = new List<Asteroid>();
        public readonly List<Explosion> Explosions = new List<Explosion>();
        public readonly string DifficultyKey;
        public int Score { get; private set; }
        public bool Dead { get; private set; }
        public string WarningText { get; private set; }
        public int WarningTimerMs => Enemies.WarningTimerMs;
        public long Ticks { get; private set; }
        private int _asteroidSpawnTimer;
        private int _lastLives = GameConstants.PlayerLives;
        private bool _expiredPending;

        // Ereignisse (für Quests, Statistik, Audio)
        public event Action<Asteroid, int> AsteroidDestroyed;
        public event Action<EnemyShip, int> EnemyDestroyed;
        public event Action<int> PlayerDamaged;     // verbleibende Leben
        public event Action PlayerDied;
        public event Action<StarSystem> SystemChanged;
        public event Action<int> ScoreChanged;

        public SinglePlayerWorld(int width, int height, string shipKey, string difficulty, ISimRandom rng = null)
        {
            Width = width; Height = height; Rng = rng ?? new SimRandom();
            DifficultyKey = Difficulties.IsValid(difficulty) ? difficulty : GameConstants.DefaultDifficulty;
            Player = new PlayerShip(ShipCatalog.Get(shipKey), width, height, Clock);
            Enemies = new EnemyManager(width, height, Player, DifficultyKey, Rng);
            Enemies.EnemyDestroyed += (e, s) => EnemyDestroyed?.Invoke(e, s);
            Background = new BackgroundDirector(width, height, Clock, Rng, true);
            Background.SystemChanged += s => SystemChanged?.Invoke(s);
            Background.NotifyScoreAnchor(0);
        }

        /// <summary>Debug-Schiffswechsel (Tasten 1–4 im Original): neues Schiff, Projektile und Gegner werden geleert.</summary>
        public void SwitchShip(string shipKey)
        {
            if (Dead) return;
            Player = new PlayerShip(ShipCatalog.Get(shipKey), Width, Height, Clock);
            _lastLives = Player.Lives;
            Lasers.Clear(); Torpedoes.Clear();
            Enemies.SetPlayer(Player, true);
        }

        private void AddScore(int amount)
        {
            if (amount == 0) return;
            Score += amount;
            ScoreChanged?.Invoke(Score);
        }

        private void DestroyAsteroid(Asteroid a)
        {
            Explosions.Add(new Explosion(a.X + a.Width / 2, a.Y + a.Height / 2, a.Scale));
        }

        /// <summary>Ein Spiel-Tick (1/60 s).</summary>
        public void Step(PlayerInput input)
        {
            Clock.Advance(GameConstants.TickMs);
            Ticks++;
            if (_expiredPending) { Explosions.RemoveAll(e => e.Timer <= 0); _expiredPending = false; }

            if (!Dead)
            {
                if (input.Laser) Lasers.AddRange(Player.Shoot());
                if (input.Torpedo) { var t = Player.FireTorpedo(); if (t != null) Torpedoes.Add(t); }
                if (input.Left) Player.MoveLeft();
                if (input.Right) Player.MoveRight(Width);
                SimulateGameplay();
                if (Player.Lives < _lastLives) { _lastLives = Player.Lives; PlayerDamaged?.Invoke(Player.Lives); }
            }

            Background.Update(Score);

            foreach (var ex in Explosions) ex.Update();
            if (Explosions.Exists(e => e.Timer <= 0)) _expiredPending = true;
            WarningText = Dead ? null : Enemies.WarningText;
        }

        private void SimulateGameplay()
        {
            for (int i = Lasers.Count - 1; i >= 0; i--) { Lasers[i].Update(); if (Lasers[i].Rect.Bottom < 0) Lasers.RemoveAt(i); }
            for (int i = Torpedoes.Count - 1; i >= 0; i--) { Torpedoes[i].Update(); if (Torpedoes[i].Rect.Bottom < 0) Torpedoes.RemoveAt(i); }

            // Asteroiden: Schwierigkeit UND aktuelles Sternensystem bestimmen Dichte, Tempo und Größe.
            var profile = Difficulties.Get(DifficultyKey);
            double systemBonus = Background.SystemBonus;
            int systemIndex = Background.SystemIndex;
            double speedMul = Background.AsteroidSpeedMultiplier * profile.AsteroidSpeed * (1.0 + systemBonus * 0.70);
            double density = profile.AsteroidDensity * (1.0 + systemBonus * 0.80);
            int interval = Math.Max(GameConstants.AsteroidMinSpawnInterval, (int)(GameConstants.AsteroidSpawnInterval / Math.Max(0.35, density)));

            _asteroidSpawnTimer++;
            if (_asteroidSpawnTimer >= interval)
            {
                Asteroids.Add(new Asteroid(Width, Height, Rng, profile.AsteroidSize * (1.0 + systemBonus * 0.18), speedMul));
                _asteroidSpawnTimer = 0;
            }
            for (int i = Asteroids.Count - 1; i >= 0; i--) { Asteroids[i].Update(); if (Asteroids[i].Y > Height) Asteroids.RemoveAt(i); }

            // Spielerschüsse gegen Asteroiden (vor dem Gegnermanager, damit ein Projektil nur einmal trifft).
            foreach (var asteroid in Asteroids.ToArray())
            {
                var rect = asteroid.GetRect();
                PlayerProjectile hit = null;
                foreach (var l in Lasers) if (rect.Colliderect(l.Rect)) { hit = l; break; }
                if (hit == null) foreach (var t in Torpedoes) if (rect.Colliderect(t.Rect)) { hit = t; break; }
                if (hit != null)
                {
                    int points = asteroid.GetPoints();
                    AddScore(points);
                    DestroyAsteroid(asteroid);
                    Asteroids.Remove(asteroid); Lasers.Remove(hit); Torpedoes.Remove(hit);
                    AsteroidDestroyed?.Invoke(asteroid, points);
                }
            }

            // Asteroiden gegen Spieler.
            foreach (var asteroid in Asteroids.ToArray())
            {
                if (!asteroid.GetRect().Colliderect(Player.Hitbox)) continue;
                if (Player.IsInvulnerable) continue;
                bool died = Player.TakeDamage();
                DestroyAsteroid(asteroid);
                Asteroids.Remove(asteroid);
                if (died) Die();
                break;
            }

            var result = Enemies.Update(GameConstants.TickSeconds, Score, systemIndex, Lasers, Torpedoes);
            AddScore(result.ScoreDelta);
            if (result.PlayerDead || Player.Lives <= 0) Die();
        }

        private void Die()
        {
            if (Dead) return;
            Dead = true;
            PlayerDied?.Invoke();
        }
    }
}
