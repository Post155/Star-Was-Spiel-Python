using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace StarWarsUnity
{
    public class PlayerShipController : MonoBehaviour
    {
        [SerializeField] private ShipDefinition shipDefinition;
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private BoxCollider2D hitbox;

        public ShipDefinition Definition => shipDefinition;
        public int Lives { get; private set; } = 3;
        public bool ShowHitbox { get; set; }
        public bool IsInvulnerable => Time.unscaledTime < _invulnerableUntil;
        public Vector2 PixelPosition { get; private set; }
        public event Action<int> LivesChanged;
        public event Action Died;
        public event Action<ProjectileController> ProjectileCreated;

        private float _invulnerableUntil;
        private const float InvulnerabilitySeconds = 2f;
        private const float BlinkInterval = 0.2f;
        private float _blinkAccumulator;
        private Camera _camera;

        public void Configure(ShipDefinition definition)
        {
            shipDefinition = definition;
            if (spriteRenderer != null && definition != null)
            {
                spriteRenderer.sprite = definition.sprite;
                transform.localScale = Vector3.one * definition.scale;
                if (definition.id == ShipId.TieFighter) transform.localRotation = Quaternion.Euler(0, 0, 180f);
            }
            _camera = Camera.main;
            Lives = 3;
            SnapToBottom();
            UpdateHitboxSize();
        }

        public void SnapToBottom()
        {
            if (shipDefinition == null || spriteRenderer == null) return;
            var bounds = spriteRenderer.bounds;
            PixelPosition = new Vector2(
                (Screen.width - bounds.size.x) * 0.5f,
                Screen.height - bounds.size.y - 20f);
            SyncTransform();
        }

        private void Update()
        {
            if (shipDefinition == null || _camera == null) return;
            float dir = 0f;
            if (Keyboard.current != null)
            {
                if (Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed) dir -= 1f;
                if (Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed) dir += 1f;
                if (Keyboard.current.spaceKey.wasPressedThisFrame || Keyboard.current.wKey.wasPressedThisFrame || Keyboard.current.upArrowKey.wasPressedThisFrame)
                    FireLaser();
                if (Keyboard.current.sKey.wasPressedThisFrame || Keyboard.current.downArrowKey.wasPressedThisFrame)
                    FireTorpedo();
            }

            PixelPosition.x += dir * shipDefinition.moveSpeed;
            float width = SpriteWidth();
            PixelPosition.x = Mathf.Clamp(PixelPosition.x, 0f, Mathf.Max(0f, Screen.width - width));
            SyncTransform();
            UpdateBlink();
        }

        public void Move(float input)
        {
            if (shipDefinition == null) return;
            PixelPosition.x += Mathf.Clamp(input, -1f, 1f) * shipDefinition.moveSpeed;
            PixelPosition.x = Mathf.Clamp(PixelPosition.x, 0f, Mathf.Max(0f, Screen.width - SpriteWidth()));
            SyncTransform();
        }

        public void FireLaser()
        {
            if (shipDefinition == null || shipDefinition.laserMuzzles == null) return;
            foreach (var local in shipDefinition.laserMuzzles)
            {
                var laser = ProjectileController.CreateLaser(this, local, -1, 1);
                ProjectileCreated?.Invoke(laser);
            }
        }

        public void FireTorpedo()
        {
            if (shipDefinition == null || !shipDefinition.canFireTorpedo) return;
            var torpedo = ProjectileController.CreateTorpedo(this, shipDefinition.torpedoMuzzle, -1, 2);
            ProjectileCreated?.Invoke(torpedo);
        }

        public bool TakeDamage(int amount = 1)
        {
            if (IsInvulnerable) return false;
            Lives = Mathf.Max(0, Lives - Mathf.Max(1, amount));
            _invulnerableUntil = Time.unscaledTime + InvulnerabilitySeconds;
            LivesChanged?.Invoke(Lives);
            if (Lives <= 0) Died?.Invoke();
            return Lives <= 0;
        }

        public void ResetLives()
        {
            Lives = 3;
            _invulnerableUntil = 0f;
            LivesChanged?.Invoke(Lives);
        }

        private void UpdateBlink()
        {
            if (spriteRenderer == null) return;
            if (!IsInvulnerable)
            {
                spriteRenderer.enabled = true;
                return;
            }

            _blinkAccumulator += Time.deltaTime;
            if (_blinkAccumulator >= BlinkInterval) _blinkAccumulator -= BlinkInterval;
            spriteRenderer.enabled = ((Time.unscaledTime * 5f) % 2f) < 1f;
        }

        private float SpriteWidth() => spriteRenderer != null ? spriteRenderer.bounds.size.x : 0f;

        private void SyncTransform()
        {
            if (spriteRenderer == null) return;
            transform.position = PixelSpace.TopLeftToWorld(PixelPosition.x, PixelPosition.y, spriteRenderer.bounds.size.x, spriteRenderer.bounds.size.y);
        }

        private void UpdateHitboxSize()
        {
            if (hitbox == null || spriteRenderer == null) return;
            var size = spriteRenderer.bounds.size;
            hitbox.size = new Vector2(size.x * 0.8f, size.y * 0.8f);
            hitbox.offset = Vector2.zero;
        }

        private void OnDrawGizmos()
        {
            if (!ShowHitbox || hitbox == null) return;
            Gizmos.color = Color.red;
            Gizmos.DrawWireCube(hitbox.bounds.center, hitbox.bounds.size);
        }
    }
}
