using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class GameSession : MonoBehaviour
    {
        public static GameSession Instance { get; private set; }
        [SerializeField] private AssetLibrary assets;
        [SerializeField] private BackgroundManager background;
        [SerializeField] private EnemyManager enemyManager;
        [SerializeField] private PlayerShipController playerPrefab;
        [SerializeField] private AsteroidController asteroidPrefab;

        public PlayerShipController Player { get; private set; }
        public int Score { get; private set; }
        public bool IsDead { get; private set; }
        public string Difficulty { get; private set; } = "normal";
        public ShipId SelectedShip { get; private set; } = ShipId.XWing;

        private Dictionary<ShipId, ShipDefinition> _ships;
        private float _asteroidSpawnCounter;
        private readonly List<AsteroidController> _asteroids = new List<AsteroidController>();
        private readonly List<ProjectileController> _playerProjectiles = new List<ProjectileController>();

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            _ships = RuntimeContent.BuildShips(assets);
        }

        public void StartSinglePlayer(ShipId ship, string difficulty)
        {
            SelectedShip = ship; Difficulty = difficulty;
            Score = 0; IsDead = false;
            if (Player != null) Destroy(Player.gameObject);
            var go = playerPrefab != null ? Instantiate(playerPrefab.gameObject) : new GameObject("Player");
            Player = go.GetComponent<PlayerShipController>() ?? go.AddComponent<PlayerShipController>();
            Player.Configure(_ships[ship]);
            Player.ProjectileCreated += RegisterProjectile;
            Player.Died += HandlePlayerDied;

            if (enemyManager == null) enemyManager = FindObjectOfType<EnemyManager>();
            if (enemyManager != null) enemyManager.Configure(Player, difficulty);
            if (background == null) background = FindObjectOfType<BackgroundManager>();
            if (background != null) { background.Initialize(assets); background.NotifyScoreAnchor(0); }
            _asteroidSpawnCounter = 0f;
            ClearObjects();
        }

        private void Update()
        {
            if (Player == null || IsDead) return;
            float systemIndex = background != null ? background.CurrentSystemIndex : 0;
            var profile = GameConstants.GetDifficulty(Difficulty);
            float systemBonus = GameConstants.GetSystemBonus((int)systemIndex);
            float density = profile.AsteroidDensity * (1f + systemBonus * .80f);
            float interval = Mathf.Max(GameConstants.AsteroidMinSpawnIntervalFrames, GameConstants.AsteroidSpawnIntervalFrames / Mathf.Max(.35f, density));
            _asteroidSpawnCounter += 1f;
            if (_asteroidSpawnCounter >= interval)
            {
                SpawnAsteroid(profile.AsteroidSize * (1f + systemBonus*.18f),
                    (background != null ? background.AsteroidSpeedMultiplier : 1f) * profile.AsteroidSpeed * (1f + systemBonus*.70f));
                _asteroidSpawnCounter = 0f;
            }

            if (background != null) background.UpdateBackground(Score);
            CleanupProjectiles();
            HandleAsteroidPlayerCollisions();
        }

        private void SpawnAsteroid(float sizeMultiplier, float speedMultiplier)
        {
            var go = asteroidPrefab != null ? Instantiate(asteroidPrefab.gameObject) : new GameObject("Asteroid");
            var asteroid = go.GetComponent<AsteroidController>() ?? go.AddComponent<AsteroidController>();
            asteroid.Destroyed += HandleAsteroidDestroyed;
            asteroid.Initialize(assets.Asteroids, sizeMultiplier, speedMultiplier);
            _asteroids.Add(asteroid);
        }

        private void RegisterProjectile(ProjectileController projectile)
        {
            if (projectile != null && !_playerProjectiles.Contains(projectile)) _playerProjectiles.Add(projectile);
        }

        private void CleanupProjectiles()
        {
            for (int i=_playerProjectiles.Count-1;i>=0;i--)
                if (_playerProjectiles[i]==null || !_playerProjectiles[i].Alive) _playerProjectiles.RemoveAt(i);
            for (int i=_asteroids.Count-1;i>=0;i--)
                if (_asteroids[i]==null || !_asteroids[i].Alive) _asteroids.RemoveAt(i);
        }

        private void HandleAsteroidPlayerCollisions()
        {
            if (Player == null || Player.IsInvulnerable) return;
            var hits = Physics2D.OverlapBoxAll(Player.transform.position, Player.GetComponent<Collider2D>()?.bounds.size ?? Vector2.one, 0f);
            foreach (var hit in hits)
            {
                var asteroid = hit.GetComponent<AsteroidController>();
                if (asteroid == null || !asteroid.Alive) continue;
                asteroid.DestroyAsteroid();
                if (Player.TakeDamage(1)) HandlePlayerDied();
                break;
            }
        }

        private void HandleAsteroidDestroyed(AsteroidController asteroid)
        {
            if (asteroid == null) return;
            AddScore(asteroid.Points);
            if (assets.Explosion != null) ExplosionController.Spawn(assets.Explosion, asteroid.transform.position, asteroid.ScaleMultiplier);
        }

        private void HandlePlayerDied() { IsDead = true; }

        public void AddScore(int amount) { Score = Mathf.Max(0, Score + amount); }
        public ShipDefinition GetShip(ShipId id) => _ships[id];

        private void ClearObjects()
        {
            foreach (var a in _asteroids) if (a != null) Destroy(a.gameObject);
            foreach (var p in _playerProjectiles) if (p != null) Destroy(p.gameObject);
            _asteroids.Clear(); _playerProjectiles.Clear();
        }
    }
}
