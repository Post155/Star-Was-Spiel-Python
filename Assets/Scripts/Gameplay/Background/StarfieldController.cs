using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class StarfieldController : MonoBehaviour
    {
        private sealed class Star
        {
            public Vector2 position; public int size; public float speed; public Color color; public bool twinkle; public int direction;
        }

        private readonly List<Star> _layer1 = new List<Star>();
        private readonly List<Star> _layer2 = new List<Star>();
        private float _density = 1f;
        private Color _tint = Color.white;

        public void Configure(float density, Color tint) { _density = Mathf.Max(.1f, density); _tint = tint; Rebuild(); }

        private void OnEnable() => Rebuild();

        private void Rebuild()
        {
            _layer1.Clear(); _layer2.Clear();
            int desired1 = Mathf.Max(50, Mathf.RoundToInt(Screen.width * Screen.height / 6000f * _density));
            int desired2 = Mathf.Max(20, Mathf.RoundToInt(Screen.width * Screen.height / 12000f * _density));
            for (int i=0;i<desired1;i++) _layer1.Add(CreateStar(1));
            for (int i=0;i<desired2;i++) _layer2.Add(CreateStar(2));
        }

        private Star CreateStar(int layer)
        {
            int size = layer == 1 ? 1 : new[] {1,2,2,3}[Random.Range(0,4)];
            float baseSpeed = layer == 1 ? .12f : .35f;
            int min = layer == 1 ? 110 : 140; int max = 255;
            float brightness = Random.Range(min, max + 1);
            Color c = new Color(brightness/255f, brightness/255f, brightness/255f);
            if (layer == 2 && Random.value < .3f) c = Color.Lerp(Color.white, _tint, .45f);
            return new Star { position = new Vector2(Random.Range(0f,Screen.width), Random.Range(0f,Screen.height)), size=size,
                speed = baseSpeed * (size/1.5f) * Random.Range(.6f,1.6f), color=c, twinkle=Random.value<.25f, direction=Random.value<.5f?-1:1 };
        }

        private void Update() { UpdateLayer(_layer1); UpdateLayer(_layer2); }

        private void UpdateLayer(List<Star> list)
        {
            foreach (var s in list)
            {
                s.position.y += s.speed;
                if (s.twinkle)
                {
                    float delta = s.direction * Random.Range(0f,3f) / 255f;
                    s.color = new Color(Mathf.Clamp01(s.color.r + delta), Mathf.Clamp01(s.color.g + delta), Mathf.Clamp01(s.color.b + delta));
                    if (s.color.r > .95f) s.direction=-1; if (s.color.r < .43f) s.direction=1;
                }
                if (s.position.y > Screen.height) { s.position.y = -s.size-2; s.position.x=Random.Range(0f,Screen.width); }
            }
        }

        private void OnRenderObject()
        {
            if (Camera.current == null) return;
            GL.PushMatrix(); GL.LoadPixelMatrix(0, Screen.width, 0, Screen.height);
            Draw(_layer1); Draw(_layer2); GL.PopMatrix();
        }

        private void Draw(List<Star> list)
        {
            Material mat = GetMaterial(); if (mat == null) return; mat.SetPass(0);
            GL.Begin(GL.QUADS);
            foreach (var s in list)
            {
                GL.Color(s.color); float x=s.position.x, y=Screen.height-s.position.y, z=s.size;
                GL.Vertex3(x,y,0); GL.Vertex3(x+z,y,0); GL.Vertex3(x+z,y-z,0); GL.Vertex3(x,y-z,0);
            }
            GL.End();
        }

        private Material _material;
        private Material GetMaterial()
        {
            if (_material != null) return _material;
            var shader = Shader.Find("Sprites/Default"); if (shader == null) return null;
            _material = new Material(shader); return _material;
        }
    }
}
