using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace StarWars.Sim
{
    /// <summary>Eine TCP-Verbindung mit eigener Sender-Warteschlange (entspricht _Connection in network.py).</summary>
    internal sealed class Connection
    {
        public readonly TcpClient Client;
        public readonly NetworkStream Stream;
        private readonly BlockingCollection<string> _queue = new BlockingCollection<string>();
        private int _closed;
        private readonly Thread _sender;
        public bool IsClosed => Volatile.Read(ref _closed) != 0;

        public Connection(TcpClient client)
        {
            Client = client; Client.NoDelay = true; Stream = client.GetStream();
            _sender = new Thread(SenderLoop) { IsBackground = true, Name = "lan-sender" };
        }

        public void StartSender() { _sender.Start(); }

        public void Send(Dictionary<string, object> payload)
        {
            if (IsClosed) return;
            string line = Json.Serialize(payload);
            if (Encoding.UTF8.GetByteCount(line) + 1 > GameConstants.MaxLineBytes) return;   // zu groß -> verwerfen
            try { _queue.Add(line); } catch (InvalidOperationException) { }
        }

        public void Close()
        {
            if (Interlocked.Exchange(ref _closed, 1) != 0) return;
            try { _queue.CompleteAdding(); } catch (Exception) { }
            try { Client.Client.Shutdown(SocketShutdown.Both); } catch (Exception) { }   // FIN sofort senden, auch wenn ein anderer Thread noch liest
            try { Client.Close(); } catch (Exception) { }
        }

        private void SenderLoop()
        {
            try
            {
                foreach (var line in _queue.GetConsumingEnumerable())
                {
                    if (IsClosed) break;
                    var data = Encoding.UTF8.GetBytes(line + "\n");
                    Stream.Write(data, 0, data.Length);
                    Stream.Flush();
                }
            }
            catch (Exception) { Close(); }
        }

        /// <summary>Liest Zeilen (JSON-Objekte). Beendet bei Verbindungsende; wirft bei Protokollverletzung.</summary>
        public IEnumerable<Dictionary<string, object>> ReadMessages()
        {
            var buffer = new List<byte>(1024);
            var chunk = new byte[4096];
            while (true)
            {
                int n;
                try { n = Stream.Read(chunk, 0, chunk.Length); }
                catch (IOException) { yield break; }
                catch (ObjectDisposedException) { yield break; }
                catch (SocketException) { yield break; }
                if (n <= 0) yield break;
                for (int i = 0; i < n; i++) buffer.Add(chunk[i]);
                if (buffer.Count > GameConstants.MaxLineBytes * 2) throw new InvalidDataException("Netzwerkpuffer ist zu groß");
                int idx;
                while ((idx = buffer.IndexOf((byte)'\n')) >= 0)
                {
                    if (idx > GameConstants.MaxLineBytes) throw new InvalidDataException("Netzwerkpaket ist zu groß");
                    if (idx == 0) { buffer.RemoveAt(0); continue; }
                    string line = Encoding.UTF8.GetString(buffer.GetRange(0, idx).ToArray());
                    buffer.RemoveRange(0, idx + 1);
                    // Unzulässige / fehlerhafte Nachrichten werden abgefangen: ungültiges JSON beendet die Verbindung (wie im Original).
                    var parsed = Json.Parse(line);
                    if (parsed is Dictionary<string, object> d) yield return d;
                }
            }
        }
    }

    /// <summary>
    /// LAN-Lobby-/Spielserver (game/network.py: LANServer). Der Server hält Spielerlisten und verteilt Snapshots;
    /// für den PvP-Modus sammelt er Eingaben und Schussereignisse, die der Host-Prozess autoritativ auswertet.
    /// </summary>
    public sealed class LanServer
    {
        public int Port { get; private set; }
        public readonly string GameMode;
        public readonly int MaxPlayers;
        private TcpListener _listener;
        private Thread _acceptThread, _broadcastThread;
        private volatile bool _stop;
        private readonly object _lock = new object();
        private readonly Dictionary<string, Connection> _connections = new Dictionary<string, Connection>();
        private readonly Dictionary<string, Dictionary<string, object>> _players = new Dictionary<string, Dictionary<string, object>>();
        private readonly List<string> _joinOrder = new List<string>();
        private string _hostId;
        private string _phase = "lobby";
        private bool _startRequested;
        private double _startedAt;
        private readonly Dictionary<string, bool[]> _pvpInputs = new Dictionary<string, bool[]>();
        private readonly Dictionary<string, List<KeyValuePair<string, long>>> _fireQueue = new Dictionary<string, List<KeyValuePair<string, long>>>();
        private readonly Dictionary<string, long> _lastFireSeq = new Dictionary<string, long>();
        private readonly Dictionary<string, double> _lastLaserAt = new Dictionary<string, double>(), _lastTorpedoAt = new Dictionary<string, double>();
        public Action<string> Log;
        /// <summary>true: Host ist ausschließlich die Loopback-Verbindung des Server-Erstellers (hello.host = true). false: erster Spieler ist Host (Verhalten des Python-Originals).</summary>
        public readonly bool ExplicitHost;

        public LanServer(int port = GameConstants.LanPort, int maxPlayers = GameConstants.MaxPlayers, string gameMode = Msg.ModePoints, bool explicitHost = false)
        {
            ExplicitHost = explicitHost; Port = port; MaxPlayers = Math.Max(1, Math.Min(GameConstants.MaxPlayers, maxPlayers)); GameMode = gameMode;
        }

        public string HostId { get { lock (_lock) return _hostId; } }
        public string Phase { get { lock (_lock) return _phase; } }
        public int PlayerCount { get { lock (_lock) return _players.Count; } }

        public void Start()
        {
            _listener = new TcpListener(IPAddress.Any, Port);
            _listener.Server.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
            _listener.Start(MaxPlayers);
            Port = ((IPEndPoint)_listener.LocalEndpoint).Port;
            _acceptThread = new Thread(AcceptLoop) { IsBackground = true, Name = "lan-accept" };
            _broadcastThread = new Thread(BroadcastLoop) { IsBackground = true, Name = "lan-broadcast" };
            _acceptThread.Start(); _broadcastThread.Start();
            Log?.Invoke("Server gestartet auf Port " + Port);
        }

        public void Stop(string reason = "server_stopped")
        {
            if (_stop) return;
            _stop = true;
            if (!string.IsNullOrEmpty(reason)) Broadcast(Proto.Make(Msg.ServerStopped, "reason", reason));
            List<Connection> conns;
            lock (_lock) { conns = new List<Connection>(_connections.Values); _connections.Clear(); _players.Clear(); }
            Thread.Sleep(60);   // Zeit, die Stop-Nachricht noch auszuliefern
            foreach (var c in conns) c.Close();
            try { _listener?.Stop(); } catch (Exception) { }
            Log?.Invoke("Server beendet");
        }

        public List<string> GetLocalAddresses()
        {
            var l = new List<string> { "127.0.0.1" };
            try { foreach (var a in Dns.GetHostEntry(Dns.GetHostName()).AddressList) if (a.AddressFamily == AddressFamily.InterNetwork && !l.Contains(a.ToString())) l.Add(a.ToString()); }
            catch (Exception) { }
            return l;
        }

        private void AcceptLoop()
        {
            while (!_stop)
            {
                TcpClient client;
                try { client = _listener.AcceptTcpClient(); }
                catch (Exception) { break; }
                var conn = new Connection(client);
                conn.StartSender();
                bool canJoin; lock (_lock) canJoin = _phase == "lobby" && _players.Count < MaxPlayers;
                if (!canJoin)
                {
                    conn.Send(Proto.Make(Msg.Error, "reason", "Lobby voll oder bereits gestartet."));
                    var t0 = new Thread(() => { Thread.Sleep(80); conn.Close(); }) { IsBackground = true }; t0.Start();
                    continue;
                }
                var t = new Thread(() => ClientLoop(conn, client.Client.RemoteEndPoint as IPEndPoint)) { IsBackground = true, Name = "lan-client" };
                t.Start();
            }
        }

        private void ClientLoop(Connection conn, IPEndPoint remote)
        {
            string playerId = null;
            try
            {
                var it = conn.ReadMessages().GetEnumerator();
                if (!it.MoveNext()) return;
                var first = it.Current;
                if (Json.Str(first, "type") != Msg.Hello) { conn.Send(Proto.Make(Msg.Error, "reason", "Ungültiger Handshake.")); Thread.Sleep(80); return; }
                if (Json.Int(first, "version", -1) != GameConstants.ProtocolVersion) { conn.Send(Proto.Make(Msg.Error, "reason", "Protokollversion passt nicht.")); Thread.Sleep(80); return; }
                string requested = Json.Str(first, "game_mode", "lan"); if (requested.Length > 24) requested = requested.Substring(0, 24);
                if (requested != GameMode) { conn.Send(Proto.Make(Msg.Error, "reason", "Dieser Server erwartet einen anderen Spielmodus.")); Thread.Sleep(80); return; }

                lock (_lock)
                {
                    if (_phase != "lobby" || _players.Count >= MaxPlayers) { conn.Send(Proto.Make(Msg.Error, "reason", "Lobby ist bereits geschlossen oder voll.")); Thread.Sleep(80); return; }
                    playerId = Guid.NewGuid().ToString("N").Substring(0, 8);
                    bool wantsHost = Json.Bool(first, "host");
                    bool loopback = remote != null && IPAddress.IsLoopback(remote.Address);
                    if (_hostId == null && (ExplicitHost ? (wantsHost && loopback) : true)) _hostId = playerId;
                    _connections[playerId] = conn; _joinOrder.Add(playerId);
                    _players[playerId] = new Dictionary<string, object>
                    {
                        { "id", playerId }, { "name", Proto.SafeName(Json.Str(first, "name")) }, { "x", 0.0 }, { "y", 0.0 }, { "width", 800L }, { "height", 600L },
                        { "ship", "xwing" }, { "score", 0L }, { "lives", 3L }, { "alive", true }, { "system", "Unbekannt" }, { "ready", false }, { "connected", true },
                        { "address", remote != null ? remote.Address.ToString() : "" },
                    };
                    _pvpInputs[playerId] = new[] { false, false };
                    _fireQueue[playerId] = new List<KeyValuePair<string, long>>();
                }
                conn.Send(Proto.Make(Msg.Welcome, "id", playerId, "host_id", HostId, "port", (long)Port, "game_mode", GameMode));
                Log?.Invoke("Player connected: " + playerId);
                BroadcastSnapshot();

                while (it.MoveNext())
                {
                    HandleMessage(playerId, it.Current);
                    if (conn.IsClosed) break;
                }
            }
            catch (Exception) { /* fehlerhafte/abgebrochene Verbindung: Spieler wird entfernt */ }
            finally
            {
                if (playerId != null) RemovePlayer(playerId);
                conn.Close();
            }
        }

        private void HandleMessage(string playerId, Dictionary<string, object> m)
        {
            string type = Json.Str(m, "type");
            switch (type)
            {
                case Msg.PointsState:
                    if (GameMode != Msg.ModePoints) return;
                    lock (_lock)
                    {
                        if (!_players.TryGetValue(playerId, out var p)) return;
                        p["x"] = Json.Num(m, "x", Convert.ToDouble(p["x"]), 0.0, 1.0);
                        p["y"] = Json.Num(m, "y", Convert.ToDouble(p["y"]), 0.0, 1.0);
                        string ship = Json.Str(m, "ship", (string)p["ship"]); p["ship"] = ship.Length > 32 ? ship.Substring(0, 32) : ship;
                        p["score"] = Json.Int(m, "score", Convert.ToInt64(p["score"]), 0, int.MaxValue);
                        string sys = Json.Str(m, "system", (string)p["system"]); p["system"] = sys.Length > 48 ? sys.Substring(0, 48) : sys;
                        p["alive"] = Json.Bool(m, "alive", true);
                    }
                    return;
                case Msg.PvpInput:
                    if (GameMode != Msg.ModePvp) return;
                    lock (_lock) if (_pvpInputs.ContainsKey(playerId)) _pvpInputs[playerId] = new[] { Json.Bool(m, "left"), Json.Bool(m, "right") };
                    return;
                case Msg.PvpFire:
                    if (GameMode != Msg.ModePvp) return;
                    {
                        string weapon = Json.Str(m, "weapon", "laser");
                        if (weapon != "laser" && weapon != "torpedo") return;
                        long seq = Json.Int(m, "sequence", 0, 0, int.MaxValue);
                        double now = Proto.EpochSeconds();
                        lock (_lock)
                        {
                            if (!_fireQueue.TryGetValue(playerId, out var q) || _phase != "game") return;
                            // Plausibilität: doppelte/verspätete Sequenznummern und unmögliche Schussfolgen verwerfen.
                            if (seq > 0)
                            {
                                _lastFireSeq.TryGetValue(playerId, out long last);
                                if (seq <= last) return;
                                _lastFireSeq[playerId] = seq;
                            }
                            var times = weapon == "laser" ? _lastLaserAt : _lastTorpedoAt;
                            double minGap = weapon == "laser" ? 0.08 : 0.20;
                            if (times.TryGetValue(playerId, out double lastAt) && now - lastAt < minGap) return;
                            times[playerId] = now;
                            if (q.Count < 16) q.Add(new KeyValuePair<string, long>(weapon, seq));
                        }
                    }
                    return;
                case Msg.Name:
                    lock (_lock) if (_players.TryGetValue(playerId, out var np)) np["name"] = Proto.SafeName(Json.Str(m, "name"));
                    BroadcastSnapshot();
                    return;
                case Msg.StartRequest:
                    lock (_lock)
                    {
                        if (playerId != _hostId || _phase != "lobby") return;
                        if (GameMode == Msg.ModePvp && _players.Count != 2)
                        {
                            if (_connections.TryGetValue(playerId, out var c)) c.Send(Proto.Make(Msg.Error, "reason", "Für PvP-Duell müssen genau zwei Spieler verbunden sein."));
                            return;
                        }
                        _phase = "setup"; _startRequested = true;
                        foreach (var p in _players.Values) p["ready"] = false;
                    }
                    Broadcast(Proto.Make(Msg.SetupStarted));
                    BroadcastSnapshot();
                    return;
                case Msg.Ready:
                    lock (_lock)
                    {
                        if (!_players.TryGetValue(playerId, out var p) || _phase != "setup") return;
                        p["ready"] = true;
                        p["name"] = Proto.SafeName(Json.Str(m, "name", (string)p["name"]));
                        string ship = Json.Str(m, "ship", "xwing"); p["ship"] = ship.Length > 32 ? ship.Substring(0, 32) : ship;
                        if (GameMode == Msg.ModePvp)
                        {
                            string rule = Json.Str(m, "game_rule", PvpModes.LastSurvivor);
                            if (PvpModes.IsValid(rule)) p["game_rule"] = rule;
                        }
                        string diff = Json.Str(m, "difficulty", ""); if (diff.Length > 0) p["difficulty"] = diff.Length > 32 ? diff.Substring(0, 32) : diff;
                    }
                    MaybeStartCountdown();
                    return;
                case Msg.Disconnect:
                    RemovePlayer(playerId);
                    return;
            }
        }

        private void MaybeStartCountdown()
        {
            double startedAt;
            lock (_lock)
            {
                if (_phase != "setup" || !_startRequested || _players.Count == 0) return;
                foreach (var p in _players.Values) if (!Json.Bool(p, "ready")) return;
                _phase = "countdown";
                _startedAt = Proto.EpochSeconds() + GameConstants.PvpStartCountdownMs / 1000.0;
                startedAt = _startedAt;
            }
            // started_at = absolute Epoch-Zeit (kompatibel zum Original); remaining_ms ist uhrenunabhängig und wird von Unity-Clients bevorzugt.
            Broadcast(Proto.Make(Msg.Countdown, "started_at", startedAt, "remaining_ms", (long)GameConstants.PvpStartCountdownMs));
        }

        private void BroadcastLoop()
        {
            while (!_stop)
            {
                var sw = System.Diagnostics.Stopwatch.StartNew();
                Dictionary<string, object> gameMsg = null;
                lock (_lock)
                    if (_phase == "countdown" && Proto.EpochSeconds() >= _startedAt) { _phase = "game"; gameMsg = Proto.Make(Msg.GameStarted); }
                if (gameMsg != null) Broadcast(gameMsg);
                BroadcastSnapshot();
                int wait = (int)Math.Max(0, GameConstants.StateBroadcastIntervalSec * 1000 - sw.ElapsedMilliseconds);
                Thread.Sleep(wait);
            }
        }

        private void BroadcastSnapshot()
        {
            string phase, host; var players = new List<object>();
            lock (_lock)
            {
                phase = _phase; host = _hostId;
                foreach (var id in _joinOrder)
                {
                    if (!_players.TryGetValue(id, out var p)) continue;
                    if (GameMode == Msg.ModePoints)
                        players.Add(new Dictionary<string, object> { { "id", p["id"] }, { "name", p["name"] }, { "x", p["x"] }, { "y", p["y"] }, { "ship", p["ship"] }, { "score", p["score"] }, { "system", p["system"] }, { "alive", p["alive"] }, { "ready", p["ready"] } });
                    else
                        players.Add(new Dictionary<string, object>(p));
                }
            }
            Broadcast(new Dictionary<string, object> { { "type", Msg.Snapshot }, { "phase", phase }, { "host_id", host }, { "players", players } });
        }

        private void Broadcast(Dictionary<string, object> payload)
        {
            List<Connection> conns;
            lock (_lock) conns = new List<Connection>(_connections.Values);
            foreach (var c in conns) c.Send(payload);
        }

        private void RemovePlayer(string playerId)
        {
            bool wasHost; Connection conn; bool existed;
            lock (_lock)
            {
                existed = _players.Remove(playerId);
                _connections.TryGetValue(playerId, out conn); _connections.Remove(playerId);
                _pvpInputs.Remove(playerId); _fireQueue.Remove(playerId); _joinOrder.Remove(playerId);
                _lastFireSeq.Remove(playerId); _lastLaserAt.Remove(playerId); _lastTorpedoAt.Remove(playerId);
                wasHost = playerId == _hostId;
                if (wasHost) _hostId = null;
            }
            conn?.Close();
            if (!existed) return;
            if (wasHost && !_stop) { Stop("Der Host hat das Spiel beendet."); return; }
            BroadcastSnapshot();
            MaybeStartCountdown();
        }

        /// <summary>Aktuelle Bewegungseingaben und alle seit dem letzten Aufruf eingegangenen Schussereignisse.</summary>
        public void ConsumePvpInputs(out Dictionary<string, bool[]> inputs, out List<KeyValuePair<string, string>> fires)
        {
            inputs = new Dictionary<string, bool[]>(); fires = new List<KeyValuePair<string, string>>();
            lock (_lock)
            {
                foreach (var kv in _pvpInputs) inputs[kv.Key] = (bool[])kv.Value.Clone();
                foreach (var kv in _fireQueue) { foreach (var f in kv.Value) fires.Add(new KeyValuePair<string, string>(kv.Key, f.Key)); kv.Value.Clear(); }
            }
        }

        public void BroadcastPvpSnapshot(Dictionary<string, object> snapshot)
        {
            if (GameMode != Msg.ModePvp) return;
            var payload = new Dictionary<string, object>(snapshot) { ["type"] = Msg.PvpSnapshot };
            Broadcast(payload);
        }
    }
}
