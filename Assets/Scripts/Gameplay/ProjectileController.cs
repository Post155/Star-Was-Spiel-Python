using UnityEngine;

namespace StarWarsUnity
{
    public enum ProjectileKind { Laser, Torpedo, EnemyLaser, EnemyTorpedo }

    public sealed class ProjectileController : MonoBehaviour
    {
        public ProjectileKind Kind { get; private set; }
        public int Damage { get; private set; }
        public string OwnerId { get; private set; }
        public float Speed { get; private set; }
        public bool Alive { get; private set; } = true;

        private Vector2 _pixelPosition;
        private int _direction;
        private SpriteRenderer _renderer;
        private BoxCollider2D _collider;

        public static ProjectileController CreateLaser(PlayerShipController owner, Vector2 localMuzzle, int direction, int damage)
        {
            var go = new GameObject("Laser");
            var projectile = go.AddComponent<ProjectileController>();
            projectile.Initialize(ProjectileKind.Laser, owner.Definition != null ? owner.Definition.name : owner.name,
                owner.Definition != null ? owner.Definition.sprite : null, damage, 15f, direction, owner, localMuzzle, false);
            return projectile;
        }

        public static ProjectileController CreateTorpedo(PlayerShipController owner, Vector2 localMuzzle, int direction, int damage)
        {
            var go = new GameObject("Torpedo");
            var projectile = go.AddComponent<ProjectileController>();
            projectile.Initialize(ProjectileKind.Torpedo, owner.Definition != null ? owner.Definition.name : owner.name,
                owner.Definition != null ? owner.Definition.torpedoSprite : null, damage, 10f, direction, owner, localMuzzle, true);
            return projectile;
        }

        public static ProjectileController CreateEnemy(ProjectileKind kind, Vector2 worldPixelPosition, Vector2 targetPixelPosition,
            int damage, float speed, Sprite sprite, string ownerId)
        {
            var go = new GameObject(kind.ToString());
            var projectile = go.AddComponent<ProjectileController>();
            projectile._renderer = go.AddComponent<SpriteRenderer>();
            projectile._collider = go.AddComponent<BoxCollider2D>();
            projectile.Kind = kind;
            projectile.Damage = damage;
            projectile.Speed = speed;
            projectile.OwnerId = ownerId;
            projectile._pixelPosition = worldPixelPosition;
            Vector2 delta = targetPixelPosition - worldPixelPosition;
            Vector2 velocity = delta.sqrMagnitude < 0.01f ? Vector2.down : delta.normalized;
            projectile._direction = 1;
            projectile._velocity = velocity * speed;
            if (sprite != null)
            {
                projectile._renderer.sprite = sprite;
                if (kind == ProjectileKind.EnemyTorpedo) projectile._renderer.transform.localRotation = Quaternion.Euler(0, 0, 180f);
            }
            projectile.SyncTransform();
            return projectile;
        }

        private Vector2 _velocity;

        private void Initialize(ProjectileKind kind, string ownerId, Sprite sprite, int damage, float speed, int direction,
            PlayerShipController owner, Vector2 localMuzzle, bool torpedo)
        {
            _renderer = gameObject.AddComponent<SpriteRenderer>();
            _collider = gameObject.AddComponent<BoxCollider2D>();
            Kind = kind;
            Damage = damage;
            Speed = speed;
            OwnerId = ownerId;
            _direction = direction < 0 ? -1 : 1;
            if (sprite != null)
            {
                _renderer.sprite = sprite;
                if (!torpedo)
                {
                    gameObject.transform.localScale = new Vector3(0.02f, 0.02f, 1f);
                    // A simple rectangular fallback matches the original 3x20 laser.
                    var sr = _renderer;
                    sr.sprite = null;
                    var texture = new Texture2D(1, 1, TextureFormat.RGBA32, false);
                    texture.SetPixel(0, 0, Color.red);
                    texture.Apply();
                    sr.sprite = Sprite.Create(texture, new Rect(0,0,1,1), new Vector2(0.5f,0.5f), 1f);
                    gameObject.transform.localScale = new Vector3(3f, 20f, 1f);
                }
            }
            else
            {
                var sr = _renderer;
                var texture = new Texture2D(1, 1, TextureFormat.RGBA32, false);
                texture.SetPixel(0, 0, torpedo ? new Color(1f, .75f, .1f) : Color.red);
                texture.Apply();
                sr.sprite = Sprite.Create(texture, new Rect(0,0,1,1), new Vector2(.5f,.5f), 1f);
                gameObject.transform.localScale = torpedo ? new Vector3(8f, 16f, 1f) : new Vector3(3f, 20f, 1f);
            }

            var ownerPos = owner.PixelPosition;
            _pixelPosition = ownerPos + localMuzzle;
            SyncTransform();
        }

        private void Update()
        {
            _pixelPosition += _velocity == Vector2.zero ? new Vector2(0f, _direction * Speed) : _velocity;
            SyncTransform();

            float margin = 100f;
            if (_pixelPosition.x < -margin || _pixelPosition.x > Screen.width + margin ||
                _pixelPosition.y < -margin || _pixelPosition.y > Screen.height + margin)
                DestroyProjectile();
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (!Alive) return;
            var asteroid = other.GetComponent<AsteroidController>();
            if (asteroid != null && (Kind == ProjectileKind.Laser || Kind == ProjectileKind.Torpedo))
            {
                asteroid.TakeProjectileHit(Damage);
                DestroyProjectile();
                return;
            }

            var enemy = other.GetComponent<EnemyController>();
            if (enemy != null && (Kind == ProjectileKind.Laser || Kind == ProjectileKind.Torpedo))
            {
                enemy.TakeDamage(Damage);
                DestroyProjectile();
                return;
            }

            var player = other.GetComponent<PlayerShipController>();
            if (player != null && (Kind == ProjectileKind.EnemyLaser || Kind == ProjectileKind.EnemyTorpedo))
            {
                player.TakeDamage(Damage);
                DestroyProjectile();
            }
        }

        private void SyncTransform()
        {
            transform.position = PixelSpace.TopLeftToWorld(_pixelPosition.x, _pixelPosition.y, 0f, 0f);
        }

        public void DestroyProjectile()
        {
            if (!Alive) return;
            Alive = false;
            Destroy(gameObject);
        }
    }
}
