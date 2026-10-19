using UnityEngine;
using UnityEngine.SceneManagement;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>
    /// Einstiegspunkt jeder Szene. Die Szenendateien enthalten nur Kamera + diese Komponente; Menüs, Spielwelten und UI werden
    /// beim Start aus dem Szenennamen aufgebaut. Dadurch ist das Projekt ohne manuelle Verdrahtung spielbar.
    /// </summary>
    public sealed class SceneBootstrap : MonoBehaviour
    {
        // Sicherheitsnetz: Wird irgendeine andere Szene (z. B. "SampleScene") gestartet, wechselt das Spiel ins Hauptmenü.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Ensure()
        {
            if (Object.FindFirstObjectByType<SceneBootstrap>() != null) return;
            string name = SceneManager.GetActiveScene().name;
            if (System.Array.IndexOf(SceneNames.All, name) < 0 && Application.CanStreamedLevelBeLoaded(SceneNames.MainMenu)) { SceneManager.LoadScene(SceneNames.MainMenu); return; }
            new GameObject("SceneBootstrap").AddComponent<SceneBootstrap>();
        }

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 1;
            AppState.EnsureServices();
        }

        private void Start()
        {
            // Die Szenen enthalten evtl. eine eigene Main Camera – sie wird für Spiel-Szenen nicht benötigt.
            string scene = SceneManager.GetActiveScene().name;
            switch (scene)
            {
                case SceneNames.Singleplayer: gameObject.AddComponent<SinglePlayerController>(); break;
                case SceneNames.LocalPointsFight: gameObject.AddComponent<PointsFightController>(); break;
                case SceneNames.LocalLastSurvivor: gameObject.AddComponent<PvpController>(); break;
                case SceneNames.LanGame:
                    if (AppState.Net != null && AppState.Net.GameMode == Msg.ModePoints) gameObject.AddComponent<LanPointsController>();
                    else gameObject.AddComponent<PvpController>();
                    break;
                case SceneNames.LanLobby: gameObject.AddComponent<MenuBackdrop>(); gameObject.AddComponent<LobbyController>(); break;
                default: gameObject.AddComponent<MenuBackdrop>(); gameObject.AddComponent<MenuScreens>(); break;
            }
            DisableSceneCameras();
        }

        private static void DisableSceneCameras()
        {
            foreach (var cam in Object.FindObjectsByType<Camera>(FindObjectsSortMode.None))
                if (cam.gameObject.name == "Main Camera") cam.enabled = false;   // eigene Kameras übernehmen das Rendering
        }
    }

    /// <summary>Animierter Sternenhintergrund für Menüs (nutzt denselben BackgroundDirector wie das Spiel).</summary>
    public sealed class MenuBackdrop : MonoBehaviour
    {
        private Stage _stage; private BackgroundDirector _bg; private SimClock _clock; private double _acc; private BackgroundView _view;

        private void Start()
        {
            int w = Mathf.RoundToInt(600f * Mathf.Max(0.5f, (float)Screen.width / Mathf.Max(1, Screen.height)));
            _clock = new SimClock();
            _bg = new BackgroundDirector(w, 600, _clock, new SimRandom(), false);
            _stage = new Stage("Menu", new Vector3(0, 0, 0), w, 600, new Rect(0, 0, 1, 1), -10);
            _view = new BackgroundView(_stage);
        }

        private void Update()
        {
            if (_stage == null) return;
            _acc += Mathf.Min(Time.unscaledDeltaTime, 0.25f);
            int n = 0;
            while (_acc >= GameConstants.TickSeconds && n++ < 4) { _clock.Advance(GameConstants.TickMs); _bg.Update(0); _acc -= GameConstants.TickSeconds; }
            _stage.Begin(); _view.Draw(_bg, false); _stage.End();
        }

        private void OnDestroy() { _stage?.Destroy(); }
    }
}
