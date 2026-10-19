using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>Nachrichtentypen des JSON-Line-Protokolls (kompatibel zu game/network.py, PROTOCOL_VERSION 1).</summary>
    public static class Msg
    {
        public const string Hello = "hello", Welcome = "welcome", Error = "error", Snapshot = "snapshot",
            PointsState = "points_state", State = "state", PvpInput = "pvp_input", PvpFire = "pvp_fire", PvpSnapshot = "pvp_snapshot",
            Name = "name", StartRequest = "start_request", SetupStarted = "setup_started", Ready = "ready", Countdown = "countdown",
            GameStarted = "game_started", ServerStopped = "server_stopped", Disconnect = "disconnect";
        public const string ModePoints = "points", ModePvp = "pvp";
    }

    public static class Proto
    {
        public static string SafeName(object value)
        {
            string name = (value == null ? "Spieler" : Convert.ToString(value)).Trim();
            if (name.Length == 0) name = "Spieler";
            return name.Length > GameConstants.MaxNameLength ? name.Substring(0, GameConstants.MaxNameLength) : name;
        }

        public static Dictionary<string, object> Make(string type, params object[] kv)
        {
            var d = new Dictionary<string, object> { { "type", type } };
            for (int i = 0; i + 1 < kv.Length; i += 2) d[(string)kv[i]] = kv[i + 1];
            return d;
        }

        /// <summary>Unix-Zeit in Sekunden (wie time.time()).</summary>
        public static double EpochSeconds() => DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
    }
}
