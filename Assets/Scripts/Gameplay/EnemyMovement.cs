using UnityEngine;

namespace StarWarsUnity
{
    public sealed class EnemyMovement
    {
        private readonly EnemyController _owner;
        public EnemyMovement(EnemyController owner) => _owner = owner;

        private static float Approach(float current, float target, float maxDelta)
        {
            return current < target ? Mathf.Min(current + maxDelta, target) : Mathf.Max(current - maxDelta, target);
        }

        public void Update(float dt, float targetX, float targetY, float dodgeVelocity)
        {
            float dx = targetX - _owner.CenterX;
            float dy = targetY - _owner.CenterY;
            float desiredVx = Mathf.Clamp(dx * 2.2f, -_owner.MaxSpeed, _owner.MaxSpeed) + dodgeVelocity;
            desiredVx = Mathf.Clamp(desiredVx, -_owner.MaxSpeed * 1.35f, _owner.MaxSpeed * 1.35f);
            float desiredVy = Mathf.Clamp(dy * 1.4f, -_owner.MaxSpeed * .55f, _owner.MaxSpeed * .55f);
            float maxChange = _owner.Acceleration * dt;
            _owner.Velocity = new Vector2(
                Approach(_owner.Velocity.x, desiredVx, maxChange),
                Approach(_owner.Velocity.y, desiredVy, maxChange * .72f));

            float magnitude = _owner.Velocity.magnitude;
            float maxTotal = _owner.MaxSpeed * 1.12f;
            if (magnitude > maxTotal) _owner.Velocity = _owner.Velocity / magnitude * maxTotal;

            _owner.PixelPosition += _owner.Velocity * dt;
            _owner.PixelPosition.x = Mathf.Clamp(_owner.PixelPosition.x, 0f, Screen.width - _owner.Width);
            float maxY = Mathf.Max(80f, Screen.height * .58f - _owner.Height);
            _owner.PixelPosition.y = Mathf.Clamp(_owner.PixelPosition.y, -_owner.Height * .15f, maxY);
            _owner.SyncTransform();
        }
    }
}
