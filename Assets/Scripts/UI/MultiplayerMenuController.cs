using UnityEngine;
using UnityEngine.SceneManagement;

namespace StarWarsUnity
{
    public sealed class MultiplayerMenuController : MonoBehaviour
    {
        public void OpenLocalPointsFight()=>SceneManager.LoadScene("LocalPointsFight");
        public void OpenLocalLastSurvivor()=>SceneManager.LoadScene("LocalLastSurvivor");
        public void OpenLan()=>SceneManager.LoadScene("LanLobby");
        public void Back()=>SceneManager.LoadScene("MainMenu");
    }
}
