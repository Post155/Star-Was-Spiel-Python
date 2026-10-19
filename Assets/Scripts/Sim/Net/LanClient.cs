using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Threading;

namespace StarWars.Sim
{
    /// <summary>
    /// Netzwerk-Client (game/network.py: LANClient). Alle Socket-Operationen laufen in Hintergrund-Threads;
    /// der Haupt-Thread ruft nur Poll() auf und verarbeitet die eingegangenen Nachrichten.
    /// </summary>
    public sealed class LanClient
    {
        private Connection _conn;
        private readonly ConcurrentQueue<Dictionary<string, object>> _incoming = new ConcurrentQueue<Dictionary<string, object>>();
        private volatile bool _stopRequested;
        private readonly object _lock = new object();
        public volatile string PlayerId, HostId, Error, Phase = "lobby";
        public volatile bool Connected, Connecting, HostDisconnected;
        public string GameMode = Msg.ModePoints;
        public Dictionary<string, Dictionary<string, object>> Players = new Dictionary<string, Dictionary<string, object>>();
        public List<string> PlayerOrder = new List<string>();
        public double CountdownRemainingMs;                   // vom Server übermittelt (uhrenunabhängig)
        public System.Diagnostics.Stopwatch CountdownClock = new System.Diagnostics.Stopwatch();
        public double StartedAtEpoch;
        public Action<string> Log;
        private volatile bool _asHost;

        public void ConnectAsync(string host, int port, string name, string gameMode, bool asHost = false)
        {
            _asHost = asHost;
            Disconnect(false);
            _stopRequested = false; Connecting = true; Error = null; HostDisconnected = false;
            GameMode = string.IsNullOrEmpty(gameMode) ? Msg.ModePoints : gameMode;
            string safe = Proto.SafeName(name);
            var t = new Thread(() => ConnectWorker(host.Trim(), port, safe)) { IsBackground = true, Name = "lan-connect" };
            t.Start();
        }

        private void ConnectWorker(string host, int port, string name)
        {
            TcpClient tcp = null;
            try
            {
                tcp = new TcpClient();
                var ar = tcp.BeginConnect(host, port, null, null);
                if (!ar.AsyncWaitHandle.WaitOne(3000)) throw new TimeoutException("Zeitüberschreitung beim Verbinden");
                tcp.EndConnect(ar);
                var conn = new Connection(tcp);
                conn.StartSender();
                _conn = conn;
                Connecting = false; Connected = true;
                var hello = Proto.Make(Msg.Hello, "version", (long)GameConstants.ProtocolVersion, "name", name, "game_mode", GameMode);
                if (_asHost) hello["host"] = true;
                conn.Send(hello);
                var rt = new Thread(ReceiveLoop) { IsBackground = true, Name = "lan-receive" };
                rt.Start();
                Log?.Invoke("Mit " + host + ":" + port + " verbunden");
            }
            catch (Exception ex)
            {
                Connecting = false; Connected = false;
                Error = "Verbindung fehlgeschlagen: " + ex.Message;
                try { tcp?.Close(); } catch (Exception) { }
            }
        }

        private void ReceiveLoop()
        {
            var conn = _conn;
            if (conn == null) return;
            try { foreach (var m in conn.ReadMessages()) { _incoming.Enqueue(m); if (conn.IsClosed || _stopRequested) break; } }
            catch (Exception) { /* Protokollfehler -> wie Verbindungsabbruch behandeln */ }
            finally
            {
                bool was = Connected;
                Connected = false;
                conn.Close();
                if (was && !_stopRequested)
                    _incoming.Enqueue(Proto.Make(Msg.ServerStopped, "reason", "Die Verbindung zum Host wurde unterbrochen."));
            }
        }

        public void Send(Dictionary<string, object> payload) { var c = _conn; if (c != null && Connected) c.Send(payload); }
        public void SendPointsState(double x, double y, string ship, int score, string system, bool alive)
            => Send(Proto.Make(Msg.PointsState, "x", PyMath.Clamp(x, 0, 1), "y", PyMath.Clamp(y, 0, 1), "ship", ship ?? "xwing", "score", (long)Math.Max(0, score), "system", system ?? "Unbekannt", "alive", alive));
        public void SendPvpInput(bool left, bool right) => Send(Proto.Make(Msg.PvpInput, "left", left, "right", right));
        public void SendPvpFire(string weapon, long sequence) => Send(Proto.Make(Msg.PvpFire, "weapon", weapon, "sequence", sequence));
        public void SendName(string name) => Send(Proto.Make(Msg.Name, "name", Proto.SafeName(name)));
        public void RequestStart() => Send(Proto.Make(Msg.StartRequest));
        public void SendReady(string name, string ship, string difficulty, string gameRule = null)
        {
            var p = Proto.Make(Msg.Ready, "name", Proto.SafeName(name), "ship", ship);
            if (difficulty != null) p["difficulty"] = difficulty;
            if (gameRule != null && PvpModes.IsValid(gameRule)) p["game_rule"] = gameRule;
            Send(p);
        }

        /// <summary>Verarbeitet alle eingegangenen Nachrichten (nur im Haupt-Thread aufrufen) und liefert sie zurück.</summary>
        public List<Dictionary<string, object>> Poll()
        {
            var events = new List<Dictionary<string, object>>();
            while (_incoming.TryDequeue(out var m)) { events.Add(m); Apply(m); }
            return events;
        }

        private void Apply(Dictionary<string, object> m)
        {
            switch (Json.Str(m, "type"))
            {
                case Msg.Welcome: PlayerId = Json.Str(m, "id"); HostId = Json.Str(m, "host_id"); break;
                case Msg.Snapshot:
                    lock (_lock)
                    {
                        Phase = Json.Str(m, "phase", Phase);
                        string h = Json.Str(m, "host_id", ""); if (h.Length > 0) HostId = h;
                        var list = Json.Arr(m, "players");
                        if (list != null)
                        {
                            var map = new Dictionary<string, Dictionary<string, object>>(); var order = new List<string>();
                            foreach (var o in list) if (o is Dictionary<string, object> d && Json.Str(d, "id").Length > 0) { map[Json.Str(d, "id")] = d; order.Add(Json.Str(d, "id")); }
                            Players = map; PlayerOrder = order;
                        }
                    }
                    break;
                case Msg.Countdown:
                    StartedAtEpoch = Json.Num(m, "started_at", 0.0);
                    CountdownRemainingMs = Json.Num(m, "remaining_ms", Math.Max(0, (StartedAtEpoch - Proto.EpochSeconds()) * 1000.0), 0, 60000);
                    CountdownClock.Restart();
                    Phase = "countdown"; break;
                case Msg.GameStarted: Phase = "game"; break;
                case Msg.SetupStarted: Phase = "setup"; break;
                case Msg.ServerStopped: HostDisconnected = true; Phase = "stopped"; Error = Json.Str(m, "reason", "Host beendet"); Connected = false; break;
                case Msg.Error: Error = Json.Str(m, "reason", "Unbekannter Netzwerkfehler"); break;
            }
        }

        public double CountdownLeftMs => Phase == "countdown" ? Math.Max(0, CountdownRemainingMs - CountdownClock.ElapsedMilliseconds) : 0;

        public void Disconnect(bool graceful = true)
        {
            if (graceful) Send(Proto.Make(Msg.Disconnect));
            _stopRequested = true;
            var c = _conn; _conn = null;
            Connected = false; Connecting = false;
            if (c != null) { if (graceful) Thread.Sleep(30); c.Close(); }
            PlayerId = null; HostId = null; Players = new Dictionary<string, Dictionary<string, object>>(); Phase = "lobby"; HostDisconnected = false;
            while (_incoming.TryDequeue(out _)) { }
        }
    }
}
