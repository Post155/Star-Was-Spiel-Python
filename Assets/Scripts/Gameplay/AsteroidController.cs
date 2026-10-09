using System;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class AsteroidController : MonoBehaviour
    {
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private CircleCollider2D hitCollider;
        public int Points { get; private set; }
        public bool Alive { get; private set; } = true;
        public float ScaleMultiplier { get; private set; }

        private Sprite[] _frames;
        private int _frame;
        private int _frameCounter;
        private float _speed;
        private float _vx;
        private float _vy;
        private Vector2 _pixelPosition;

        public event Action<AsteroidController> Destroyed;

        public void Initialize(Sprite[] frames, float sizeMultiplier, float speedMultiplier)
        {
            _frames = frames;
            ScaleMultiplier = Mathf.Clamp(UnityEngine.Random.value < 0.25f ? .25f : UnityEngine.Random.value < .33f ? .5f : UnityEngine.Random.value < .5f ? .75f : 1f, .18f, 1.25f) * sizeMultiplier;
            _speed = UnityEngine.Random.Range(GameConstants.AsteroidMinSpeed, GameConstants.AsteroidMaxSpeed) * speedMultiplier;
            _vy = _speed;
            _vx = 0f;
            _frame = 0;
            _frameCounter = 0;
            if (_frames == null || _frames.Length == 0) return;
            ApplyFrame();
            float width = SpriteWidth();
            _pixelPosition = new Vector2(UnityEngine.Random.Range(0f, Mathf.Max(0f, Screen.width - width)), -SpriteHeight());
            SyncTransform();
            Points = ScaleMultiplier <= .5f ? 100 : ScaleMultiplier <= .75f ? 75 : 50;
        }

        private void Update()
        {
            if (!Alive) return;
            _pixelPosition += new Vector2(_vx, _vy);
            _frameCounter++;
            if (_frameCounter >= 5)
            {
                _frameCounter = 0;
                _frame = (_frame + 1) % (_frames == null || _frames.Length == 0 ? 1 : _frames.Length);
                ApplyFrame();
            }
            SyncTransform();
            if (_pixelPosition.y > Screen.height + SpriteHeight()) DestroyAsteroid();
        }

        public void TakeProjectileHit(int _damage)
        {
            if (!Alive) return;
            DestroyAsteroid();
        }

        public Rect PixelRect()
        {
            float w = SpriteWidth();
            float h = SpriteHeight();
            return new Rect(_pixelPosition.x + w * .15f, _pixelPosition.y + h * .15f, w * .7f, h * .7f);
        }

        private float SpriteWidth() => spriteRenderer != null ? spriteRenderer.bounds.size.x : 0f;
        private float SpriteHeight() => spriteRenderer != null ? spriteRenderer.bounds.size.y : 0f;

        private void ApplyFrame()
        {
            if (spriteRenderer == null) return;
            spriteRenderer.sprite = _frames[_frame];
            transform.localScale = Vector3.one * ScaleMultiplier * (Screen.height / 600f);
            if (hitCollider != null) hitCollider.radius = Mathf.Max(SpriteWidth(), SpriteHeight()) * .35f;
        }

        private void SyncTransform() => transform.position = PixelSpace.TopLeftToWorld(_pixelPosition.x, _pixelPosition.y, SpriteWidth(), SpriteHeight());

        public void DestroyAsteroid()
        {
            if (!Alive) return;
            Alive = false;
            Destroyed?.Invoke(this);
            Destroy(gameObject);
        }
    }
}
