using UnityEngine;
using UnityEngine.SceneManagement;

namespace StarWarsUnity
{
    public sealed class DeathScreenController : MonoBehaviour
    {
        public void Restart() => SceneManager.LoadScene(SceneManager.GetActiveScene().name);
        public void BackToMenu() => SceneManager.LoadScene("MainMenu");
    }
}
