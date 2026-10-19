using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>Anzeige-Daten eines entfernten Spielers (Ghost) – rein visuell, keine Hitbox.</summary>
    public sealed class RemotePlayer
    {
        public string Id, Name, Ship = "xwing", System = "Unbekannt";
        public double X, Y, TargetX, TargetY;   // normiert 0..1
        public int Score; public bool Alive = true, Ready;
        public void Interpolate(double f = 0.28) { X += (TargetX - X) * f; Y += (TargetY - Y) * f; }
    }

    /// <summary>
    /// Hochebene des Mehrspielers (game/multiplayer.py): besitzt ggf. den Server, immer genau einen Client
    /// (der Host verbindet sich selbst über 127.0.0.1, damit Lobby-/Spielpfade für alle identisch sind).
    /// </summary>
    public sealed class MultiplayerSession
    {
        public LanServer Server { get; private set; }
        public readonly LanClient Client = new LanClient();
        public readonly string GameMode;
        public readonly int MaxPlayers;
        public readonly Dictionary<string, RemotePlayer> Remote = new Dictionary<string, RemotePlayer>();
        public string LocalName = "Spieler", Error;
        public bool Hosting { get; private set; }
        private DateTime _lastSend = DateTime.MinValue;

        public MultiplayerSession(string gameMode, int maxPlayers = GameConstants.MaxPlayers)
        {
            GameMode = gameMode; MaxPlayers = Math.Max(1, Math.Min(GameConstants.MaxPlayers, maxPlayers));
        }

        public string LocalId => Client.PlayerId;
        public bool Connected => Client.Connected;
        public bool Connecting => Client.Connecting;
        public string Phase => Client.Phase;
        public string HostId => Client.HostId;
        public Dictionary<string, Dictionary<string, object>> Players => Client.Players;
        public bool IsHost => !string.IsNullOrEmpty(LocalId) && LocalId == HostId;
        public int Port => Server != null ? Server.Port : GameConstants.LanPort;

        public void Host(string name, int port = GameConstants.LanPort)
        {
            LocalName = string.IsNullOrWhiteSpace(name) ? "Host" : name.Trim();
            Server = new LanServer(port, MaxPlayers, GameMode, true);
            Server.Start();
            Hosting = true;
            Client.ConnectAsync("127.0.0.1", Server.Port, LocalName, GameMode, true);
        }

        public void Join(string host, string name, int port = GameConstants.LanPort)
        {
            LocalName = string.IsNullOrWhiteSpace(name) ? "Spieler" : name.Trim();
            Hosting = false;
            Client.ConnectAsync(host, port, LocalName, GameMode);
        }

        public void RequestStart() => Client.RequestStart();
        public void SendReady(string ship, string difficulty, string gameRule = null) => Client.SendReady(LocalName, ship, difficulty, gameRule);

        public List<Dictionary<string, object>> Poll()
        {
            var events = Client.Poll();
            if (!string.IsNullOrEmpty(Client.Error)) Error = Client.Error;
            var seen = new HashSet<string>();
            foreach (var kv in Client.Players)
            {
                if (kv.Key == LocalId) continue;
                seen.Add(kv.Key);
                if (!Remote.TryGetValue(kv.Key, out var r)) { r = new RemotePlayer { Id = kv.Key, X = 0.5, Y = 0.35 }; Remote[kv.Key] = r; }
                var d = kv.Value;
                r.Name = Json.Str(d, "name", "Spieler"); r.Ship = Json.Str(d, "ship", r.Ship);
                r.TargetX = Json.Num(d, "x", 0.5, 0, 1); r.TargetY = Json.Num(d, "y", 0.85, 0, 1);
                r.Score = (int)Json.Int(d, "score", 0, 0, int.MaxValue); r.System = Json.Str(d, "system", "Unbekannt");
                r.Alive = Json.Bool(d, "alive", true); r.Ready = Json.Bool(d, "ready");
                r.Interpolate();
            }
            foreach (var id in new List<string>(Remote.Keys)) if (!seen.Contains(id)) Remote.Remove(id);
            return events;
        }

        /// <summary>Punktekampf: lokalen Zustand (normiert) höchstens alle 50 ms senden. Der Server speichert nur Anzeigedaten.</summary>
        public void UpdateLocalPoints(PlayerShip ship, int score, string system, bool alive, bool force = false)
        {
            var now = DateTime.UtcNow;
            if (!force && (now - _lastSend).TotalMilliseconds < GameConstants.PvpInputIntervalMs) return;
            _lastSend = now;
            Client.SendPointsState((double)ship.X / GameConstants.Width, (double)ship.Y / GameConstants.Height, ship.Info.Key, score, system, alive);
        }

        public List<Dictionary<string, object>> ScoreboardRows(int localScore, bool localAlive)
        {
            var rows = new List<Dictionary<string, object>>();
            foreach (var id in Client.PlayerOrder) if (Client.Players.TryGetValue(id, out var p)) { var row = new Dictionary<string, object>(p); row["id"] = id; rows.Add(row); }
            if (LocalId != null && !Client.Players.ContainsKey(LocalId))
                rows.Add(new Dictionary<string, object> { { "id", LocalId }, { "name", LocalName }, { "score", (long)localScore }, { "alive", localAlive } });
            rows.Sort((a, b) => Json.Int(b, "score").CompareTo(Json.Int(a, "score")));
            return rows;
        }

        public void Stop(bool graceful = true)
        {
            Client.Disconnect(graceful);
            if (Server != null) { Server.Stop("Der Host hat das Spiel beendet."); Server = null; }
            Remote.Clear(); Hosting = false;
        }
    }
}
