using System.Collections.Generic;
using UnityEngine;

namespace StarWars.Game
{
    public enum Sfx { Laser, Torpedo, Explosion, Hit, Warning, Click }

    /// <summary>
    /// Das Python-Original enthält keine Audiodateien (kein pygame.mixer-Aufruf). Damit der Port trotzdem hörbar ist,
    /// werden schlichte Effekte zur Laufzeit synthetisiert und über AudioSource abgespielt. Eigene Clips lassen sich
    /// unter Resources/Audio/&lt;Name&gt; (laser, torpedo, explosion, hit, warning, click) ablegen und haben Vorrang.
    /// </summary>
    public sealed class SoundBank : MonoBehaviour
    {
        private static SoundBank _instance;
        private readonly Dictionary<Sfx, AudioClip> _clips = new Dictionary<Sfx, AudioClip>();
        private AudioSource[] _sources;
        private int _next;

        public static SoundBank Instance
        {
            get
            {
                if (_instance != null) return _instance;
                var go = new GameObject("SoundBank");
                Object.DontDestroyOnLoad(go);
                _instance = go.AddComponent<SoundBank>();
                _instance.Init();
                return _instance;
            }
        }

        private void Init()
        {
            _sources = new AudioSource[8];
            for (int i = 0; i < _sources.Length; i++) { _sources[i] = gameObject.AddComponent<AudioSource>(); _sources[i].playOnAwake = false; }
            _clips[Sfx.Laser] = Resources.Load<AudioClip>("Audio/laser") ?? Tone("laser", 0.12f, 900f, 300f, 0.35f, false);
            _clips[Sfx.Torpedo] = Resources.Load<AudioClip>("Audio/torpedo") ?? Tone("torpedo", 0.25f, 220f, 90f, 0.45f, false);
            _clips[Sfx.Explosion] = Resources.Load<AudioClip>("Audio/explosion") ?? Tone("explosion", 0.35f, 140f, 40f, 0.5f, true);
            _clips[Sfx.Hit] = Resources.Load<AudioClip>("Audio/hit") ?? Tone("hit", 0.2f, 180f, 60f, 0.5f, true);
            _clips[Sfx.Warning] = Resources.Load<AudioClip>("Audio/warning") ?? Tone("warning", 0.4f, 660f, 660f, 0.3f, false);
            _clips[Sfx.Click] = Resources.Load<AudioClip>("Audio/click") ?? Tone("click", 0.05f, 500f, 400f, 0.25f, false);
        }

        private static AudioClip Tone(string name, float seconds, float f0, float f1, float volume, bool noise)
        {
            const int rate = 22050;
            int n = Mathf.Max(1, (int)(seconds * rate));
            var data = new float[n];
            var rng = new System.Random(name.GetHashCode());
            float phase = 0f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)n;
                float f = Mathf.Lerp(f0, f1, t);
                phase += 2f * Mathf.PI * f / rate;
                float s = noise ? (float)(rng.NextDouble() * 2.0 - 1.0) * 0.7f + Mathf.Sin(phase) * 0.3f : Mathf.Sign(Mathf.Sin(phase)) * 0.5f + Mathf.Sin(phase) * 0.5f;
                data[i] = s * volume * (1f - t) * (1f - t);
            }
            var clip = AudioClip.Create(name, n, 1, rate, false);
            clip.SetData(data, 0);
            return clip;
        }

        public static void Play(Sfx sfx, float volume = 1f)
        {
            var inst = Instance;
            if (!inst._clips.TryGetValue(sfx, out var clip) || clip == null) return;
            var src = inst._sources[inst._next++ % inst._sources.Length];
            src.PlayOneShot(clip, volume);
        }
    }
}
