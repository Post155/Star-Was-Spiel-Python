using UnityEngine;

namespace StarWarsUnity
{
    [RequireComponent(typeof(Camera))]
    public sealed class PixelCamera : MonoBehaviour
    {
        private Camera _camera;
        private int _lastWidth;
        private int _lastHeight;

        private void Awake()
        {
            _camera = GetComponent<Camera>();
            Apply();
        }

        private void LateUpdate()
        {
            if (_lastWidth != Screen.width || _lastHeight != Screen.height)
                Apply();
        }

        private void Apply()
        {
            _lastWidth = Screen.width;
            _lastHeight = Screen.height;
            PixelSpace.ConfigureCamera(_camera);
        }
    }
}
