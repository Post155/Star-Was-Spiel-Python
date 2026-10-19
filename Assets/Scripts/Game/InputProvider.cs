using UnityEngine;
using StarWars.Sim;

namespace StarWars.Game
{
    public enum ControlScheme { Solo, Player1Wasd, Player2Arrows }

    /// <summary>
    /// Ersetzt pygame.key/pygame.event: Bewegung ist Zustand (gedrückt gehalten), Schüsse sind Ereignisse (KEYDOWN).
    /// Ereignisse werden pro Frame gesammelt (Update) und im nächsten 60-Hz-Tick einmalig verbraucht.
    /// Nutzt den Legacy Input Manager (Projekteinstellung "Active Input Handling" = Input Manager oder Both).
    /// </summary>
    public sealed class InputAccumulator
    {
        private readonly ControlScheme _scheme;
        private bool _laserPending, _torpedoPending;
        public InputAccumulator(ControlScheme scheme) { _scheme = scheme; }

#if ENABLE_LEGACY_INPUT_MANAGER
        private static bool Down(KeyCode k) => Input.GetKeyDown(k);
        private static bool Held(KeyCode k) => Input.GetKey(k);
#else
        private static bool Down(KeyCode k) => false;
        private static bool Held(KeyCode k) => false;
#endif

        /// <summary>Pro Frame aufrufen.</summary>
        public void Sample()
        {
            switch (_scheme)
            {
                case ControlScheme.Solo:
                    if (Down(KeyCode.Space) || Down(KeyCode.W) || Down(KeyCode.UpArrow)) _laserPending = true;
                    if (Down(KeyCode.S) || Down(KeyCode.DownArrow)) _torpedoPending = true; break;
                case ControlScheme.Player1Wasd:
                    if (Down(KeyCode.W)) _laserPending = true;
                    if (Down(KeyCode.S)) _torpedoPending = true; break;
                default:
                    if (Down(KeyCode.UpArrow)) _laserPending = true;
                    if (Down(KeyCode.DownArrow)) _torpedoPending = true; break;
            }
        }

        /// <summary>Pro Simulations-Tick aufrufen: liefert Zustand + verbrauchte Ereignisse.</summary>
        public PlayerInput Take()
        {
            var p = new PlayerInput();
            switch (_scheme)
            {
                case ControlScheme.Solo: p.Left = Held(KeyCode.A) || Held(KeyCode.LeftArrow); p.Right = Held(KeyCode.D) || Held(KeyCode.RightArrow); break;
                case ControlScheme.Player1Wasd: p.Left = Held(KeyCode.A); p.Right = Held(KeyCode.D); break;
                default: p.Left = Held(KeyCode.LeftArrow); p.Right = Held(KeyCode.RightArrow); break;
            }
            p.Laser = _laserPending; p.Torpedo = _torpedoPending;
            _laserPending = false; _torpedoPending = false;
            return p;
        }

        public static bool KeyDown(KeyCode k) => Down(k);
        public static bool KeyHeld(KeyCode k) => Held(k);
    }
}
