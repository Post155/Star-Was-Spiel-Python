using UnityEngine;

namespace StarWarsUnity
{
    public sealed class CombatSystem : MonoBehaviour
    {
        public static CombatSystem Instance { get; private set; }
        private void Awake(){ if(Instance!=null && Instance!=this){Destroy(gameObject);return;} Instance=this; }

        public int ApplyDamage(PlayerShipController target, int damage)
        {
            if (target == null) return 0;
            bool died = target.TakeDamage(damage);
            return died ? 1 : 0;
        }

        public bool ApplyDamage(EnemyController target, int damage)
        {
            return target != null && target.TakeDamage(damage);
        }
    }
}
