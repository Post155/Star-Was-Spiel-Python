using System;
using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class EnemyController : MonoBehaviour
    {
        public EnemyArchetype Archetype { get; private set; }
        public bool IsAlive { get; private set; } = true;
        public string Role { get; set; }
        public Vector2 PixelPosition { get; set; }
        public Vector2 Velocity { get; set; }
        public float Width => _sprite != null ? _sprite.bounds.size.x : 0f;
        public float Height => _sprite != null ? _sprite.bounds.size.y : 0f;
        public float CenterX => PixelPosition.x + Width * .5f;
        public float CenterY => PixelPosition.y + Height * .5f;
        public float MaxSpeed { get; private set; }
        public float Acceleration { get; private set; }
        public float CurrentDodgeChance => Archetype != null ? Archetype.dodgeChance : 0f;
        public float EstimatedPlayerVX { get; private set; }
        public Bounds HitboxBounds => _collider != null ? _collider.bounds : new Bounds(transform.position, Vector3.one);

        private SpriteRenderer _sprite;
        private BoxCollider2D _collider;
        private EnemyBrain _brain;
        private EnemyMovement _movement;
        private EnemyWeaponSystem _weapons;
        private float _hp;
        private float _damageFlash;
        private float _previousPlayerX = float.NaN;
        private int _maxHp;

        public event Action<EnemyController, int> Destroyed;

        public void Initialize(Sprite sprite, EnemyArchetype archetype, Vector2 spawn, string role, float difficultyScale, Sprite torpedoSprite)
        {
            _sprite = GetComponent<SpriteRenderer>();
            _collider = GetComponent<BoxCollider2D>() ?? gameObject.AddComponent<BoxCollider2D>();
            _sprite.sprite = sprite;
            transform.localRotation = Quaternion.Euler(0, 0, 180f);
            Archetype = CopyAndScale(archetype, difficultyScale);
            Role = role;
            _maxHp = Archetype.maxHp;
            _hp = _maxHp;
            MaxSpeed = Archetype.maxSpeed;
            Acceleration = Archetype.acceleration;
            PixelPosition = spawn;
            transform.localScale = Vector3.one * Archetype.visualScaleMultiplier;
            _brain = new EnemyBrain(this, role);
            _movement = new EnemyMovement(this);
            _weapons = new EnemyWeaponSystem(this, torpedoSprite);
            SyncTransform();
        }

        private static EnemyArchetype CopyAndScale(EnemyArchetype original, float scale)
        {
            var clone = ScriptableObject.Instantiate(original);
            clone.maxHp = Mathf.Max(1, Mathf.RoundToInt(original.maxHp));
            clone.maxSpeed = original.maxSpeed;
            clone.acceleration = original.acceleration;
            return clone;
        }

        public List<ProjectileController> UpdateAI(float dt, PlayerShipController player, IReadOnlyList<ProjectileController> projectiles,
            IReadOnlyList<EnemyController> nearby, float difficultyScale)
        {
            var result = new List<ProjectileController>();
            if (!IsAlive) return result;
            if (!float.IsNaN(_previousPlayerX) && dt > 0f)
            {
                float instantaneous = (player.PixelPosition.x - _previousPlayerX) / dt;
                EstimatedPlayerVX = EstimatedPlayerVX * .78f + instantaneous * .22f;
            }
            _previousPlayerX = player.PixelPosition.x;
            Vector3 target = _brain.Update(dt, player, projectiles, nearby, difficultyScale);
            _movement.Update(dt, target.x, target.y, target.z);
            _damageFlash = Mathf.Max(0f, _damageFlash - dt);
            SetFlash(_damageFlash > 0f);
            result.AddRange(_weapons.Update(dt, player, difficultyScale));
            return result;
        }

        public bool TakeDamage(int amount)
        {
            if (!IsAlive) return false;
            int effective = Mathf.Max(1, Mathf.RoundToInt(amount * (1f - Archetype.armorResistance)));
            _hp -= effective;
            _damageFlash = .11f;
            if (_hp <= 0f)
            {
                _hp = 0f;
                IsAlive = false;
                int bonus = Random.Range(Archetype.bonusScore.x, Archetype.bonusScore.y + 1);
                Destroyed?.Invoke(this, Archetype.baseScore + bonus);
                Destroy(gameObject);
                return true;
            }
            return false;
        }

        private void SetFlash(bool active)
        {
            if (_sprite == null) return;
            _sprite.color = active ? new Color(.55f, .55f, .55f, 1f) : Color.white;
        }

        public void SyncTransform()
        {
            transform.position = PixelSpace.TopLeftToWorld(PixelPosition.x, PixelPosition.y, Width, Height);
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (!IsAlive) return;
            var player = other.GetComponent<PlayerShipController>();
            if (player != null)
            {
                player.TakeDamage(1);
                TakeDamage(_maxHp);
            }
        }
    }
}
