using UnityEngine;

namespace StarWarsUnity
{
    public static class PixelSpace
    {
        public static Vector3 TopLeftToWorld(float x, float y, float width = 0f, float height = 0f)
        {
            float worldY = Screen.height - (y + height * 0.5f);
            return new Vector3(x + width * 0.5f, worldY, 0f);
        }

        public static Vector2 WorldToTopLeft(Vector3 world, float width, float height)
        {
            return new Vector2(world.x - width * 0.5f, Screen.height - world.y - height * 0.5f);
        }

        public static void ConfigureCamera(Camera camera)
        {
            if (camera == null) return;
            camera.orthographic = true;
            camera.orthographicSize = Screen.height * 0.5f;
            camera.transform.position = new Vector3(Screen.width * 0.5f, Screen.height * 0.5f, -100f);
        }
    }
}
