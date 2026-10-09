using UnityEngine;

namespace StarWarsUnity
{
    public sealed class ExplosionController : MonoBehaviour
    {
        private float _remaining;
        private SpriteRenderer _renderer;

        public static ExplosionController Spawn(Sprite sprite, Vector2 pixelPosition, float scale, float duration = 0.5f)
        {
            var go = new GameObject("Explosion");
            var fx = go.AddComponent<ExplosionController>();
            fx._renderer = go.AddComponent<SpriteRenderer>();
            fx._renderer.sprite = sprite;
            go.transform.position = PixelSpace.TopLeftToWorld(pixelPosition.x, pixelPosition.y);
            go.transform.localScale = Vector3.one * Mathf.Max(.1f, scale * .85f);
            fx._remaining = duration;
            return fx;
        }

        private void Update()
        {
            _remaining -= Time.deltaTime;
            if (_remaining <= 0f) Destroy(gameObject);
        }
    }
}
