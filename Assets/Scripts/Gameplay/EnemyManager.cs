using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class EnemyManager : MonoBehaviour
    {
        [SerializableEnemyList] private List<EnemyArchetype> archetypes = new List<EnemyArchetype>();
        [SerializeField] private AssetLibrary assets;
        [SerializeField] private EnemyController enemyPrefab;

        public int ScoreDelta { get; private set; }
        public string WarningText { get; private set; }
        public float WarningRemaining { get; private set; }
        public readonly List<EnemyController> ActiveEnemies = new List<EnemyController>();
        public readonly List<ProjectileController> Projectiles = new List<ProjectileController>();

        private PlayerShipController _player;
        private string _difficulty = "normal";
        private System.Func<int> _scoreGetter;
        private System.Action<int> _scoreAdder;
        private float _spawnTimer = 1f;
        private int _roleCursor;
        private readonly HashSet<int> _warnedTiers = new HashSet<int>();
        private int _pendingTier;

        public void Configure(PlayerShipController player, string difficulty, System.Func<int> scoreGetter = null, System.Action<int> scoreAdder = null)
        {
            _player = player;
            _difficulty = difficulty;
            _scoreGetter = scoreGetter;
            _scoreAdder = scoreAdder;
            if (archetypes == null || archetypes.Count == 0) archetypes = RuntimeContent.BuildEnemyArchetypes();
            if (assets == null) assets = FindObjectOfType<AssetLibrary>();
            ScoreDelta = 0;
        }

        private void Update()
        {
            if (_player == null || _player.Lives <= 0) return;
            ScoreDelta = 0;
            float systemIndex = 0f;
            int currentScore = _scoreGetter != null ? _scoreGetter() : (GameSession.Instance != null ? GameSession.Instance.Score : 0);
            float scale = DifficultyScale(currentScore, (int)systemIndex);
            if (WarningRemaining > 0f)
            {
                WarningRemaining -= Time.deltaTime * 1000f;
                if (WarningRemaining <= 0f) { _warnedTiers.Add(_pendingTier); _pendingTier = 0; WarningText = null; }
            }
            CheckUnlockWarning(currentScore);
            _spawnTimer -= Time.deltaTime;
            if (_pendingTier == 0 && _spawnTimer <= 0f)
            {
                int score = currentScore;
                int cap = MaxEnemies(score, (int)systemIndex);
                if (ActiveEnemies.Count < cap)
                {
                    var archetype = ChooseArchetype(score, (int)systemIndex);
                    if (archetype != null) Spawn(archetype, scale);
                }
                _spawnTimer = SpawnInterval(score, (int)systemIndex);
            }

            for (int i = ActiveEnemies.Count - 1; i >= 0; i--)
            {
                var enemy = ActiveEnemies[i];
                if (enemy == null || !enemy.IsAlive) { ActiveEnemies.RemoveAt(i); continue; }
                var spawned = enemy.UpdateAI(Time.deltaTime, _player, Projectiles, ActiveEnemies, scale);
                for (int s = 0; s < spawned.Count; s++) Projectiles.Add(spawned[s]);
            }

            for (int i = Projectiles.Count - 1; i >= 0; i--)
            {
                if (Projectiles[i] == null) Projectiles.RemoveAt(i);
            }
        }

        private int UnlockedTier(int score) => score >= GameConstants.EnemyUnlockElitePoints ? 3 : score >= GameConstants.EnemyUnlockHeavyPoints ? 2 : score >= GameConstants.EnemyUnlockStandardPoints ? 1 : 0;
        private void CheckUnlockWarning(int score)
        {
            if (_pendingTier != 0) return;
            int tier = UnlockedTier(score);
            for (int newTier = 1; newTier <= 3; newTier++)
            {
                if (tier < newTier || _warnedTiers.Contains(newTier)) continue;
                _pendingTier = newTier;
                WarningText = newTier == 1 ? "Achtung! Feindliche Schiffe wurden entdeckt." : newTier == 2 ? "Warnung: Schwere Feinde im Anflug!" : "WARNUNG: Elite-Einheit im Anflug!";
                WarningRemaining = GameConstants.EnemyWarningDurationMs;
                return;
            }
        }

        private float DifficultyScale(int score, int systemIndex)
        {
            var p = GameConstants.GetDifficulty(_difficulty);
            float progress = score > GameConstants.EnemyUnlockStandardPoints
                ? Mathf.Min(GameConstants.SystemProgressMaxBonus, (score - GameConstants.EnemyUnlockStandardPoints) / 5000f * GameConstants.SystemProgressMaxBonus)
                : 0f;
            return Mathf.Max(.75f, 1f + GameConstants.GetSystemBonus(systemIndex) + progress);
        }

        private int MaxEnemies(int score, int systemIndex)
        {
            var p = GameConstants.GetDifficulty(_difficulty);
            float scale = DifficultyScale(score, systemIndex);
            int baseCount = 1 + Mathf.Min(5, Mathf.Max(0, score - 1000) / 1800);
            int cap = Mathf.RoundToInt(baseCount * p.EnemyMax * (1f + (scale - 1f) * .45f));
            return Mathf.Clamp(cap, 1, 8);
        }

        private float SpawnInterval(int score, int systemIndex)
        {
            var p = GameConstants.GetDifficulty(_difficulty);
            float scale = DifficultyScale(score, systemIndex);
            float pressure = 1f + Mathf.Max(0f, scale - 1f) * .45f;
            float interval = 2.60f * p.EnemySpawn / pressure;
            if (score < GameConstants.EnemyUnlockHeavyPoints) interval += .55f;
            if (score < GameConstants.EnemyUnlockElitePoints) interval += .25f;
            return Mathf.Max(1.15f, interval) * Random.Range(.90f, 1.12f);
        }

        private EnemyArchetype ChooseArchetype(int score, int systemIndex)
        {
            int tier = UnlockedTier(score);
            if (tier <= 0 || archetypes.Count == 0) return null;
            float roll = Random.value;
            EnemyArchetype Find(string key) => archetypes.Find(a => a != null && a.key == key);
            if (tier == 1) return roll < .30f ? Find("fast") : Find("standard");
            if (tier == 2) return roll < .14f ? Find("fast") : roll < .36f ? Find("heavy") : Find("standard");
            return roll < .10f ? Find("elite") : roll < .34f ? Find("heavy") : roll < .56f ? Find("fast") : Find("standard");
        }

        private void Spawn(EnemyArchetype archetype, float scale)
        {
            var go = enemyPrefab != null ? Instantiate(enemyPrefab.gameObject) : new GameObject("Enemy");
            var enemy = go.GetComponent<EnemyController>() ?? go.AddComponent<EnemyController>();
            float width = Screen.width;
            float x = Random.Range(0f, Mathf.Max(0f, width - 96f));
            float y = Random.Range(-20f, Screen.height * .18f);
            string[] roles = { "attacker", "flanker_left", "flanker_right", "support" };
            string role = roles[_roleCursor++ % roles.Length];
            Sprite sprite = AssetSpriteFor(archetype);
            enemy.Initialize(sprite, archetype, new Vector2(x, y), role, scale, assets != null ? assets.Torpedo : null);
            enemy.Destroyed += HandleEnemyDestroyed;
            ActiveEnemies.Add(enemy);
        }

        private Sprite AssetSpriteFor(EnemyArchetype archetype)
        {
            // Faction opposition is resolved by GameSession's current player ship.
            if (GameSession.Instance == null || GameSession.Instance.Player == null || assets == null) return assets != null ? assets.TieFighter : null;
            switch (GameSession.Instance.Player.Definition.id)
            {
                case ShipId.XWing: return assets.TieFighter;
                case ShipId.MillenniumFalcon: return assets.BattleDroid;
                case ShipId.TieFighter: return assets.XWing;
                default: return assets.MillenniumFalcon;
            }
        }

        private void HandleEnemyDestroyed(EnemyController enemy, int value)
        {
            ScoreDelta += value;
            if (_scoreAdder != null) _scoreAdder(value); else if (GameSession.Instance != null) GameSession.Instance.AddScore(value);
        }
    }

    public sealed class SerializableEnemyList : PropertyAttribute { }
}
