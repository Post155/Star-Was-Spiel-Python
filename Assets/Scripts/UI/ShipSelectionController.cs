using UnityEngine;
using UnityEngine.SceneManagement;

namespace StarWarsUnity
{
    public sealed class ShipSelectionController : MonoBehaviour
    {
        public void SelectXWing() => Select(ShipId.XWing);
        public void SelectMillenniumFalcon() => Select(ShipId.MillenniumFalcon);
        public void SelectTieFighter() => Select(ShipId.TieFighter);
        public void SelectBattleDroid() => Select(ShipId.BattleDroid);

        private void Select(ShipId id)
        {
            PlayerPrefs.SetString("ship", id.ToString());
            PlayerPrefs.Save();
            SceneManager.LoadScene("Singleplayer");
        }
    }
}
