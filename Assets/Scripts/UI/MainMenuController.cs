using UnityEngine;
using UnityEngine.SceneManagement;

namespace StarWarsUnity
{
    public sealed class MainMenuController : MonoBehaviour
    {
        public void OpenSingleplayer() => SceneManager.LoadScene("Singleplayer");
        public void OpenMultiplayer() => SceneManager.LoadScene("MultiplayerMenu");
        public void QuitGame() => Application.Quit();
    }
}
