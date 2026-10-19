using System;
using System.IO;
using System.Linq;

namespace StarWars.SimTests
{
    public static class Program
    {
        public static int Main(string[] args)
        {
            string golden = args.Length > 0 ? args[0] : Path.Combine("Tests", "Golden", "golden.json");
            string report = args.Length > 1 ? args[1] : null;
            T.Run("Golden", () => GoldenTests.Run(golden));
            T.Run("Gameplay", GameplayTests.Run);
            T.Run("Netzwerk", NetworkTests.Run);
            Console.WriteLine($"\nErgebnis: {T.Passed} bestanden, {T.Failed} fehlgeschlagen");
            if (report != null) File.WriteAllText(report, string.Join("\n", T.Log) + $"\n\n**Gesamt: {T.Passed} bestanden, {T.Failed} fehlgeschlagen**\n");
            return T.Failed == 0 ? 0 : 1;
        }
    }
}
