using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class EnemyBrain
    {
        private static readonly Dictionary<string, float> RoleOffsets = new Dictionary<string, float>
        {
            ["attacker"] = 0f, ["support"] = .18f, ["flanker_left"] = -.26f, ["flanker_right"] = .26f
        };
        private static readonly Dictionary<string, float> RoleY = new Dictionary<string, float>
        {
            ["attacker"] = .34f, ["support"] = .18f, ["flanker_left"] = .27f, ["flanker_right"] = .27f
        };

        private readonly EnemyController _owner;
        private float _reactionTimer;
        private float _dodgeTime;
        private float _dodgeVelocity;
        private float _dodgeLockout;
        private float _targetX;
        private float _targetY;
        private float _jitter;

        private static float RoleValue(Dictionary<string,float> map, string key, float fallback)
            => map.TryGetValue(key, out var value) ? value : fallback;

        public EnemyBrain(EnemyController owner, string role)
        {
            _owner = owner;
            _owner.Role = role;
            _reactionTimer = Random.Range(owner.Archetype.reactionTime.x, owner.Archetype.reactionTime.y);
            _targetX = owner.CenterX;
            _targetY = Screen.height * RoleValue(RoleY, role, .28f);
            _jitter = Random.Range(-55f, 55f);
            _dodgeLockout = Random.Range(.35f, .8f);
        }

        private bool ProjectileThreat(ProjectileController projectile)
        {
            if (projectile == null) return false;
            Vector2 p = projectile.transform.position;
            float verticalDistance = _owner.HitboxBounds.bottom - p.y;
            if (verticalDistance >= 0f) return false;
            float speed = Mathf.Max(60f, projectile.Speed * 60f);
            float time = Mathf.Abs(verticalDistance) / speed;
            if (time > .72f) return false;
            float margin = 22f + Mathf.Abs(_owner.Velocity.x) * Mathf.Min(.20f, time);
            return p.x >= _owner.HitboxBounds.left - margin && p.x <= _owner.HitboxBounds.right + margin;
        }

        private void ChooseDodge(IReadOnlyList<ProjectileController> projectiles, IReadOnlyList<EnemyController> nearby)
        {
            if (_dodgeLockout > 0f) return;
            bool threatened = false;
            for (int i = 0; i < projectiles.Count; i++)
            {
                if (ProjectileThreat(projectiles[i])) { threatened = true; break; }
            }
            if (!threatened) return;
            if (Random.value > _owner.CurrentDodgeChance)
            {
                _dodgeLockout = Random.Range(.2f, .55f);
                return;
            }

            float leftSpace = _owner.PixelPosition.x;
            float rightSpace = Screen.width - (_owner.PixelPosition.x + _owner.Width);
            int direction = leftSpace > rightSpace ? -1 : 1;
            for (int i = 0; i < nearby.Count; i++)
            {
                var other = nearby[i];
                if (other == null || other == _owner || !other.IsAlive) continue;
                if (Mathf.Abs(other.CenterY - _owner.CenterY) < _owner.Height * 1.5f)
                {
                    if (other.CenterX - _owner.CenterX > 0 && other.CenterX - _owner.CenterX < _owner.Width * 2f) direction = -1;
                    else if (_owner.CenterX - other.CenterX > 0 && _owner.CenterX - other.CenterX < _owner.Width * 2f) direction = 1;
                }
            }
            if (Random.value < .25f) direction *= -1;
            _dodgeVelocity = direction * _owner.MaxSpeed * Random.Range(1.05f, 1.35f);
            _dodgeTime = Random.Range(.20f, .46f);
            _dodgeLockout = Random.Range(.65f, 1.35f);
        }

        public Vector3 Update(float dt, PlayerShipController player, IReadOnlyList<ProjectileController> projectiles,
            IReadOnlyList<EnemyController> nearby, float difficultyScale)
        {
            _reactionTimer -= dt;
            _dodgeLockout = Mathf.Max(0f, _dodgeLockout - dt);
            if (_dodgeTime > 0f) _dodgeTime -= dt;
            else _dodgeVelocity *= Mathf.Max(0f, 1f - 7f * dt);

            if (_reactionTimer <= 0f && player != null)
            {
                float playerX = player.PixelPosition.x + player.transform.lossyScale.x * .5f;
                float roleOffset = RoleValue(RoleOffsets, _owner.Role, 0f) * Screen.width;
                float lead = _owner.EstimatedPlayerVX * (.10f + _owner.Archetype.accuracy * .18f);
                _jitter = Random.Range(-1f, 1f) * (80f * (1f - _owner.Archetype.accuracy));
                _targetX = playerX + roleOffset + lead + _jitter;
                _targetY = Screen.height * RoleValue(RoleY, _owner.Role, .28f);
                if (_owner.Role == "attacker" && Random.value < .17f) _targetY = Screen.height * Random.Range(.38f, .50f);
                else if (_owner.Role == "support") _targetY = Screen.height * Random.Range(.13f, .23f);
                ChooseDodge(projectiles, nearby);

                float reactionFactor = Mathf.Max(.72f, 1f / Mathf.Max(1f, difficultyScale * .08f + 1f));
                _reactionTimer = Random.Range(_owner.Archetype.reactionTime.x, _owner.Archetype.reactionTime.y) * reactionFactor;
            }

            return new Vector3(_targetX, _targetY, _dodgeVelocity);
        }
    }
}
