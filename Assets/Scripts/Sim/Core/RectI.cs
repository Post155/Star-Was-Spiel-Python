using System;

namespace StarWars.Sim
{
    /// <summary>
    /// Ersatz für pygame.Rect (ganzzahlig, Ursprung oben links, y wächst nach unten).
    /// Bildet die Semantik von Pygame nach: Float-Argumente werden abgeschnitten (trunc),
    /// center = x + w/2 (Ganzzahldivision), colliderect ist offen am rechten/unteren Rand.
    /// </summary>
    public struct RectI
    {
        public int X, Y, W, H;

        public RectI(int x, int y, int w, int h) { X = x; Y = y; W = w; H = h; }

        /// <summary>pygame.Rect(float, float, float, float): jede Komponente wird einzeln abgeschnitten.</summary>
        public static RectI FromFloats(double x, double y, double w, double h)
            => new RectI((int)Math.Truncate(x), (int)Math.Truncate(y), (int)Math.Truncate(w), (int)Math.Truncate(h));

        /// <summary>surface.get_rect(center=(cx, cy)): Pygame rundet die Float-Mitte (am Original gemessen: 505.52 -> 506), dann x = cx - w//2.</summary>
        public static RectI FromCenter(double cx, double cy, int w, int h)
            => new RectI(PyMath.Round(cx) - w / 2, PyMath.Round(cy) - h / 2, w, h);

        public int Left => X;
        public int Top => Y;
        public int Right => X + W;
        public int Bottom => Y + H;
        public int CenterX => X + W / 2;
        public int CenterY => Y + H / 2;

        public bool Colliderect(RectI o)
            => X < o.X + o.W && o.X < X + W && Y < o.Y + o.H && o.Y < Y + H;

        public RectI Inflate(int dx, int dy) => new RectI(X - dx / 2, Y - dy / 2, W + dx, H + dy);

        public RectI Union(RectI o)
        {
            int l = Math.Min(X, o.X), t = Math.Min(Y, o.Y);
            int r = Math.Max(Right, o.Right), b = Math.Max(Bottom, o.Bottom);
            return new RectI(l, t, r - l, b - t);
        }

        public override string ToString() => $"RectI({X},{Y},{W},{H})";
    }

    public static class PyMath
    {
        /// <summary>Pythons round(): Banker's Rounding (Halbwerte zur geraden Zahl).</summary>
        public static int Round(double v) => (int)Math.Round(v, MidpointRounding.ToEven);

        public static double Clamp(double v, double lo, double hi) => v < lo ? lo : (v > hi ? hi : v);

        public static int ClampInt(int v, int lo, int hi) => v < lo ? lo : (v > hi ? hi : v);

        /// <summary>pygame.transform.scale_by: Zielgröße wird abgeschnitten.</summary>
        public static int ScaleDim(int dim, double factor) => (int)Math.Truncate(dim * factor);
    }
}
