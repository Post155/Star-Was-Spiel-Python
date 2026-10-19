using System.IO;
using NUnit.Framework;
using UnityEngine;

namespace StarWars.SimTests
{
    /// <summary>
    /// Unity Test Runner (EditMode): führt dieselbe Testsuite aus wie der Konsolen-Runner (Tests/ConsoleRunner).
    /// Fenster: Window > General > Test Runner > EditMode > Run All.
    /// </summary>
    public class SimSuiteTests
    {
        private static string GoldenPath => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Tests", "Golden", "golden.json"));

        [Test] public void Golden_Parity_Mit_Python_Original()
        {
            T.Reset(); GoldenTests.Run(GoldenPath);
            Assert.AreEqual(0, T.Failed, string.Join("\n", T.Failures));
        }

        [Test] public void Gameplay_Regeln_Speicher_Inventar_Quests()
        {
            T.Reset(); GameplayTests.Run();
            Assert.AreEqual(0, T.Failed, string.Join("\n", T.Failures));
        }

        [Test, Timeout(120000)] public void LAN_Netzwerk_Loopback()
        {
            T.Reset(); NetworkTests.Run();
            Assert.AreEqual(0, T.Failed, string.Join("\n", T.Failures));
        }
    }
}
