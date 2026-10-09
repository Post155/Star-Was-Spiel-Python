using UnityEngine;
using UnityEngine.InputSystem;

namespace StarWarsUnity
{
    public readonly struct PlayerInputState
    {
        public readonly float Move; public readonly bool Laser; public readonly bool Torpedo;
        public PlayerInputState(float move,bool laser,bool torpedo){Move=move;Laser=laser;Torpedo=torpedo;}
    }

    public sealed class LocalInputRouter : MonoBehaviour
    {
        public PlayerInputState ReadPlayer1()
        {
            var k=Keyboard.current; if(k==null)return new PlayerInputState(0,false,false);
            float m=(k.aKey.isPressed?-1:0)+(k.dKey.isPressed?1:0);
            return new PlayerInputState(m,k.wKey.wasPressedThisFrame||k.spaceKey.wasPressedThisFrame,k.sKey.wasPressedThisFrame);
        }
        public PlayerInputState ReadPlayer2()
        {
            var k=Keyboard.current; if(k==null)return new PlayerInputState(0,false,false);
            float m=(k.leftArrowKey.isPressed?-1:0)+(k.rightArrowKey.isPressed?1:0);
            return new PlayerInputState(m,k.upArrowKey.wasPressedThisFrame,k.downArrowKey.wasPressedThisFrame);
        }
    }
}
