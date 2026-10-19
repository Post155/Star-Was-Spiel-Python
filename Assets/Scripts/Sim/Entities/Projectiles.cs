namespace StarWars.Sim
{
    /// <summary>Basis für Projektile des Spielers (Laser/Torpedo). Entspricht game/entities/projectiles.py.</summary>
    public abstract class PlayerProjectile
    {
        public RectI Rect;
        public int Speed;
        public int Direction = -1;      // -1 = nach oben (Bildschirm), +1 = nach unten
        public string OwnerId;
        public string Id;
        public abstract bool IsTorpedo { get; }
        public void Update() { Rect.Y += Speed * Direction; }
    }

    public sealed class Laser : PlayerProjectile
    {
        public Laser(double x, double y, int direction = -1, string ownerId = null)
        {
            Rect = RectI.FromFloats(x, y, 3, 20);
            Speed = 15;
            Direction = direction < 0 ? -1 : 1;
            OwnerId = ownerId;
        }
        public override bool IsTorpedo => false;
    }

    public sealed class Torpedo : PlayerProjectile
    {
        public Torpedo(double x, double y, int direction = -1, string ownerId = null)
        {
            int w = PyMath.ScaleDim(AssetMetrics.TorpedoBaseWidth, 0.50);
            int h = PyMath.ScaleDim(AssetMetrics.TorpedoBaseHeight, 0.50);
            Rect = RectI.FromCenter(x + 4, y + 10, w, h);
            Speed = 10;
            Direction = direction < 0 ? -1 : 1;
            OwnerId = ownerId;
        }
        public override bool IsTorpedo => true;
    }
}
