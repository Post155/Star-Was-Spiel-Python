using System;
using System.Collections.Generic;
using System.IO;

namespace StarWars.SimTests
{
    /// <summary>Winziger Test-Harness ohne externe Pakete (läuft überall mit dem .NET SDK, auch offline).</summary>
    public static class T
    {
        public static int Passed, Failed;
        public static readonly List<string> Log = new List<string>();
        public static readonly List<string> Failures = new List<string>();
        public static void Reset() { Passed = 0; Failed = 0; Log.Clear(); Failures.Clear(); }
        public static string Section = "";

        public static void Group(string name) { Section = name; Console.WriteLine("\n== " + name); Log.Add("\n## " + name); }

        public static void Check(string name, bool ok, string detail = "")
        {
            if (ok) { Passed++; Console.WriteLine("  PASS  " + name); Log.Add("- PASS  " + name); }
            else { Failed++; Failures.Add(name + " " + detail); Console.WriteLine("  FAIL  " + name + "  " + detail); Log.Add("- **FAIL**  " + name + "  " + detail); }
        }

        public static void Near(string name, double actual, double expected, double tol = 1e-9)
            => Check(name, Math.Abs(actual - expected) <= tol, $"erwartet {expected}, erhalten {actual}");

        public static void Eq<TV>(string name, TV actual, TV expected)
            => Check(name, EqualityComparer<TV>.Default.Equals(actual, expected), $"erwartet {expected}, erhalten {actual}");

        public static void Run(string name, Action a)
        {
            try { a(); }
            catch (Exception ex) { Failed++; Failures.Add(name + ": " + ex.Message); Console.WriteLine("  FAIL  " + name + " -> Ausnahme: " + ex); Log.Add("- **FAIL**  " + name + " Ausnahme: " + ex.GetType().Name + ": " + ex.Message); }
        }
    }
}
