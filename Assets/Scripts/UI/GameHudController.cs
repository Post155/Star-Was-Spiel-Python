using UnityEngine;
using UnityEngine.UI;

namespace StarWarsUnity
{
    public sealed class GameHudController : MonoBehaviour
    {
        [SerializeField] private Text scoreText;
        [SerializeField] private Text systemText;
        [SerializeField] private Text warningText;
        [SerializeField] private Text gameOverText;
        [SerializeField] private Slider livesBar;

        private void Update()
        {
            var session = GameSession.Instance;
            if (session == null) return;
            if (scoreText != null) scoreText.text = $"Punkte: {session.Score}";
            if (systemText != null) systemText.text = FindObjectOfType<BackgroundManager>()?.CurrentSystemName ?? "";
            if (livesBar != null && session.Player != null) { livesBar.maxValue = 3; livesBar.value = session.Player.Lives; }
            if (warningText != null)
            {
                var enemies = FindObjectOfType<EnemyManager>();
                warningText.text = enemies != null ? enemies.WarningText ?? string.Empty : string.Empty;
            }
            if (gameOverText != null) gameOverText.gameObject.SetActive(session.IsDead);
        }
    }
}
