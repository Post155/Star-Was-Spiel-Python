using UnityEngine;
using UnityEngine.SceneManagement;

namespace StarWarsUnity
{
    public sealed class FactionSelectionController : MonoBehaviour
    {
        public void SelectRebels() => SceneManager.LoadScene("ShipSelection");
        public void SelectEmpire() => SceneManager.LoadScene("ShipSelection");
        public void Back() => SceneManager.LoadScene("MainMenu");
    }
}
