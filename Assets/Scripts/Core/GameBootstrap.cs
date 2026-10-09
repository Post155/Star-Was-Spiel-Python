using UnityEngine;

namespace StarWarsUnity
{
    public sealed class GameBootstrap : MonoBehaviour
    {
        [SerializeField] private AssetLibrary assets;
        [SerializeField] private Camera gameCamera;
        [SerializeField] private BackgroundManager background;

        private void Awake()
        {
            if (gameCamera == null) gameCamera = Camera.main;
            PixelSpace.ConfigureCamera(gameCamera);
        }

        private void Start()
        {
            if (GameSession.Instance == null) return;
            var ship = (ShipId)System.Enum.Parse(typeof(ShipId), PlayerPrefs.GetString("ship", "XWing"));
            string difficulty = PlayerPrefs.GetString("difficulty", "normal");
            GameSession.Instance.StartSinglePlayer(ship, difficulty);
        }
    }
}
