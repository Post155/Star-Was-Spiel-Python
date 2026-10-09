using UnityEngine;

namespace StarWarsUnity
{
    public sealed class BackgroundManager : MonoBehaviour
    {
        [SerializeField] private StarfieldController starfield;
        [SerializeField] private StarSystemManager systems;
        private AssetLibrary _assets;
        private PlanetController _planet;
        private float _lastSwitchScore;
        private float _lastSwitchTime;
        private bool _transitionActive;
        private float _transitionRemaining;
        private int _transitionTarget;

        public string CurrentSystemName => systems != null && systems.Current != null ? systems.Current.idName : string.Empty;
        public int CurrentSystemIndex => systems != null ? systems.CurrentIndex : 0;
        public float CurrentSystemBonus => GameConstants.GetSystemBonus(CurrentSystemIndex);
        public float AsteroidSpeedMultiplier => systems != null && systems.Current != null ? systems.Current.asteroidSpeedMultiplier : 1f;
        public bool IsTransitioning => _transitionActive;

        public void Initialize(AssetLibrary assets)
        {
            _assets=assets;
            if (systems==null) systems=GetComponent<StarSystemManager>()??gameObject.AddComponent<StarSystemManager>();
            systems.Initialize(assets); ApplyCurrentVisuals(); _lastSwitchTime=Time.unscaledTime;
        }

        public void NotifyScoreAnchor(int score){_lastSwitchScore=score;_lastSwitchTime=Time.unscaledTime;}

        public void UpdateBackground(int score)
        {
            if (!_transitionActive && (score-(int)_lastSwitchScore>=GameConstants.SystemSwitchPoints || (Time.unscaledTime-_lastSwitchTime)*1000f>=GameConstants.SystemSwitchTimeMs)) StartTransition(score);
            if (_transitionActive)
            {
                _transitionRemaining -= Time.deltaTime*1000f;
                if (_transitionRemaining<=0f){systems.AdvanceToIndex(_transitionTarget);_transitionActive=false;_lastSwitchScore=score;_lastSwitchTime=Time.unscaledTime;ApplyCurrentVisuals();}
            }
            SpawnPlanetWhenAllowed();
        }

        private void ApplyCurrentVisuals()
        {
            if (starfield!=null && systems.Current!=null) starfield.Configure(systems.Current.starDensity, systems.Current.starTint);
        }

        private void SpawnPlanetWhenAllowed()
        {
            if (_planet!=null || systems.Current==null || systems.Current.planetSprites==null || systems.Current.planetSprites.Length==0) return;
            float timeInSystem=(Time.unscaledTime-_lastSwitchTime)*1000f;
            float timeUntil=(GameConstants.SystemSwitchTimeMs-(Time.unscaledTime-_lastSwitchTime)*1000f);
            if (timeInSystem<=10000f || timeUntil<=10000f) return;
            var go=new GameObject("Planet"); _planet=go.AddComponent<PlanetController>();
            _planet.Initialize(systems.Current.planetSprites[Random.Range(0,systems.Current.planetSprites.Length)], Random.Range(.3f,.7f), Random.Range(.35f,.7f));
        }

        private void StartTransition(int score){_transitionActive=true;_transitionRemaining=GameConstants.GalaxyMapDurationMs;_transitionTarget=systems.NextIndex();_lastSwitchScore=score;_lastSwitchTime=Time.unscaledTime; if(_planet!=null){_planet.StartExit();_planet=null;}}

        private void OnRenderObject()
        {
            if (!_transitionActive || Camera.current==null) return;
            Material m = new Material(Shader.Find("Sprites/Default")); m.SetPass(0); GL.PushMatrix(); GL.LoadPixelMatrix(0,Screen.width,0,Screen.height);
            GL.Begin(GL.QUADS); GL.Color(new Color(0,0,0,.45f)); GL.Vertex3(0,0,0); GL.Vertex3(Screen.width,0,0); GL.Vertex3(Screen.width,Screen.height,0); GL.Vertex3(0,Screen.height,0); GL.End();
            GL.PopMatrix(); Destroy(m);
        }
    }
}
