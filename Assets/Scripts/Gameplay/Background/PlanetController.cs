using UnityEngine;

namespace StarWarsUnity
{
    public sealed class PlanetController : MonoBehaviour
    {
        private SpriteRenderer _renderer;
        private float _speed;
        private float _drift;
        private bool _exiting;

        public void Initialize(Sprite sprite, float speed, float scale)
        {
            _renderer = gameObject.AddComponent<SpriteRenderer>(); _renderer.sprite = sprite;
            transform.localScale = Vector3.one * scale;
            _speed = speed; _drift = Random.Range(-.15f,.15f);
            transform.position = PixelSpace.TopLeftToWorld(Random.Range(50f, Mathf.Max(50f,Screen.width-_renderer.bounds.size.x)), -_renderer.bounds.size.y, _renderer.bounds.size.x, _renderer.bounds.size.y);
        }

        public void StartExit() { _exiting = true; _speed=Mathf.Max(_speed,2f); }

        private void Update()
        {
            Vector3 p=transform.position; p.y -= _speed * (_exiting?4f:1f); p.x += _drift * (_exiting?2f:1f); transform.position=p;
            if (Screen.height - p.y < -_renderer.bounds.size.y || p.y < -Screen.height) Destroy(gameObject);
        }
    }
}
