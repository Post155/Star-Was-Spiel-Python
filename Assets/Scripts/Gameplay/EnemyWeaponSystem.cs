using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class EnemyWeaponSystem
    {
        private readonly EnemyController _owner;
        private float _laserTimer;
        private float _torpedoTimer;
        private int _burstRemaining;
        private float _burstTimer;
        private readonly Sprite _torpedoSprite;

        public EnemyWeaponSystem(EnemyController owner, Sprite torpedoSprite)
        {
            _owner = owner;
            _torpedoSprite = torpedoSprite;
            _laserTimer = Random.Range(.35f, 1.2f);
            _torpedoTimer = Random.Range(owner.Archetype.torpedoCooldown.x, owner.Archetype.torpedoCooldown.y);
        }

        private Vector2 AimPoint(PlayerShipController player, float difficultyScale)
        {
            float distanceY = Mathf.Max(1f, player.PixelPosition.y - _owner.PixelPosition.y);
            float flightTime = Mathf.Min(.75f, distanceY / 470f);
            float accuracy = Mathf.Min(.97f, _owner.Archetype.accuracy + .015f * difficultyScale);
            float prediction = _owner.EstimatedPlayerVX * flightTime * accuracy;
            float spread = (1f - accuracy) * 160f;
            return new Vector2(player.PixelPosition.x + prediction + Random.Range(-spread, spread),
                player.PixelPosition.y + Random.Range(-10f, 18f));
        }

        private ProjectileController FireLaser(PlayerShipController player, float difficultyScale)
        {
            Vector2 target = AimPoint(player, difficultyScale);
            Vector2 muzzle = new Vector2(_owner.CenterX + Random.Range(-1, 2) * _owner.Width * .12f, _owner.PixelPosition.y + _owner.Height - 4f);
            return ProjectileController.CreateEnemy(ProjectileKind.EnemyLaser, muzzle, target,
                _owner.Archetype.laserDamage, 470f + Mathf.Min(90f, difficultyScale * 8f), null, _owner.name);
        }

        public List<ProjectileController> Update(float dt, PlayerShipController player, float difficultyScale)
        {
            var spawned = new List<ProjectileController>();
            if (player == null) return spawned;
            _laserTimer -= dt;
            _torpedoTimer -= dt;
            _burstTimer -= dt;
            if (player.PixelPosition.y <= _owner.PixelPosition.y) return spawned;

            if (_burstRemaining > 0 && _burstTimer <= 0f)
            {
                spawned.Add(FireLaser(player, difficultyScale));
                _burstRemaining--;
                _burstTimer = Random.Range(.08f, .16f);
            }

            if (_burstRemaining <= 0 && _laserTimer <= 0f)
            {
                _burstRemaining = Random.Range(_owner.Archetype.burstRange.x, _owner.Archetype.burstRange.y + 1);
                _burstTimer = 0f;
                _laserTimer = Random.Range(_owner.Archetype.laserCooldown.x, _owner.Archetype.laserCooldown.y) * Mathf.Max(.58f, 1f - difficultyScale * .035f);
            }

            bool aligned = player.PixelPosition.y > _owner.PixelPosition.y && Mathf.Abs(player.PixelPosition.x - _owner.CenterX) <= Mathf.Max(55f, _owner.Width * .72f);
            if (_torpedoTimer <= 0f && aligned && Random.value < Mathf.Min(.92f, _owner.Archetype.torpedoChance + difficultyScale * .018f))
            {
                Vector2 target = AimPoint(player, difficultyScale);
                spawned.Add(ProjectileController.CreateEnemy(ProjectileKind.EnemyTorpedo,
                    new Vector2(_owner.CenterX, _owner.PixelPosition.y + _owner.Height), target,
                    _owner.Archetype.torpedoDamage, 285f + Mathf.Min(55f, difficultyScale * 5f), _torpedoSprite, _owner.name));
            }
            if (_torpedoTimer <= 0f)
                _torpedoTimer = Random.Range(_owner.Archetype.torpedoCooldown.x, _owner.Archetype.torpedoCooldown.y) / Mathf.Max(1f, 1f + difficultyScale * .03f);

            return spawned;
        }
    }
}
