using System;

namespace StarWars.Sim
{
    /// <summary>Zufallsquelle der Simulation (austauschbar, damit Tests deterministisch laufen).</summary>
    public interface ISimRandom
    {
        double NextDouble();                       // random.random()
        double Uniform(double a, double b);        // random.uniform(a, b)
        int Int(int a, int b);                     // random.randint(a, b) – beide Grenzen inklusive
    }

    public sealed class SimRandom : ISimRandom
    {
        private readonly Random _r;
        public SimRandom() { _r = new Random(); }
        public SimRandom(int seed) { _r = new Random(seed); }
        public double NextDouble() => _r.NextDouble();
        public double Uniform(double a, double b) => a + (b - a) * _r.NextDouble();
        public int Int(int a, int b) => b < a ? a : a + _r.Next(b - a + 1);
    }

    public static class RandomExt
    {
        public static T Choice<T>(this ISimRandom r, params T[] items) => items[r.Int(0, items.Length - 1)];
        public static void Shuffle<T>(this ISimRandom r, System.Collections.Generic.IList<T> list)
        {
            for (int i = list.Count - 1; i > 0; i--)
            {
                int j = r.Int(0, i);
                T t = list[i]; list[i] = list[j]; list[j] = t;
            }
        }
    }
}
