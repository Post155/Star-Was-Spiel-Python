using UnityEngine;
using UnityEngine.SceneManagement;

namespace StarWarsUnity
{
    public sealed class DifficultySelectionController : MonoBehaviour
    {
        public void SelectEasy() { Start("easy"); }
        public void SelectNormal() { Start("normal"); }
        public void SelectHard() { Start("hard"); }
        public void SelectExpert() { Start("expert"); }

        private void Start(string key)
        {
            // Store difficulty in PlayerPrefs; the runtime session consumes the same key.
            PlayerPrefs.SetString("difficulty", key);
            PlayerPrefs.Save();
            SceneManager.LoadScene("ShipSelection");
        }
    }
}
