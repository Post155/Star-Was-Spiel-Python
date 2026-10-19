using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    /// <summary>Darstellungsdaten eines Spielers aus einem Snapshot (Client-Seite).</summary>
    public sealed class DuelViewPlayer
    {
        public string Id, Name, Ship, Role;
        public double X, Y, TargetX, TargetY;
        public int Width = 80, Height = 80, Score, Lives = 3, Kills, Hits, Shots, Damage, SurvivalMs;
        public bool Alive = true, Eliminated, Invulnerable;
        private bool _init;
        public void SetTarget(double x, double y)
        {
            if (!_init) { X = x; Y = y; _init = true; }
            TargetX = x; TargetY = y;
        }
        public void Smooth(double f = 0.35) { X += (TargetX - X) * f; Y += (TargetY - Y) * f; }
    }

    public sealed class ViewAsteroid { public string Id; public double X, Y, Scale; public int Width, Height, Frame; }
    public sealed class ViewProjectile { public string Id, OwnerId, Weapon; public double X, Y; public int Width, Height; }
    public sealed class ViewEffect { public string Id; public double X, Y, Scale; public int AgeMs; public double SeenAtMs; }

    /// <summary>Client-Sicht auf eine PvP-Partie: wendet Host-Snapshots an (game/pvp_duel.py: _apply_snapshot). Der Client simuliert nichts selbst.</summary>
    public sealed class PvpClientView
    {
        public readonly SimClock Clock = new SimClock();
        public readonly BackgroundDirector Background;
        public readonly Dictionary<string, DuelViewPlayer> Players = new Dictionary<string, DuelViewPlayer>();
        public readonly List<string> PlayerOrder = new List<string>();
        public List<ViewAsteroid> Asteroids = new List<ViewAsteroid>();
        public List<ViewProjectile> Projectiles = new List<ViewProjectile>();
        public readonly Dictionary<string, ViewEffect> Effects = new Dictionary<string, ViewEffect>();
        public string Mode = PvpModes.LastSurvivor;
        public int MatchElapsedMs, SourceWidth = 800, SourceHeight = 600;
        public bool MatchOver; public Dictionary<string, object> Result;
        public double ResultStartedMs;
        public bool HostStopped;
        private List<string> _lastOrder = new List<string>();
        private string _lastTransitionSig;
        public long SnapshotsApplied { get; private set; }

        public PvpClientView(ISimRandom rng = null) { Background = new BackgroundDirector(GameConstants.Width, GameConstants.Height, Clock, rng ?? new SimRandom(), false); }

        public void Tick()
        {
            Clock.Advance(GameConstants.TickMs);
            Background.Update(0);
            foreach (var p in Players.Values) p.Smooth(0.35);
            foreach (var id in new List<string>(Effects.Keys)) if (Clock.NowMs - Effects[id].SeenAtMs + Effects[id].AgeMs > GameConstants.PvpExplosionDurationMs) Effects.Remove(id);
        }

        public void ApplySnapshot(Dictionary<string, object> s)
        {
            SnapshotsApplied++;
            Mode = PvpModes.IsValid(Json.Str(s, "mode")) ? Json.Str(s, "mode") : Mode;
            SourceWidth = (int)Json.Int(s, "source_width", 800, 320, 10000); SourceHeight = (int)Json.Int(s, "source_height", 600, 240, 10000);
            MatchElapsedMs = (int)Json.Int(s, "match_elapsed_ms", MatchElapsedMs, 0, int.MaxValue);

            var order = new List<string>();
            var ord = Json.Arr(s, "system_order"); if (ord != null) foreach (var o in ord) order.Add(Convert.ToString(o));
            if (order.Count > 0 && !SameList(order, _lastOrder)) { _lastOrder = order; Background.SetSystemOrderByIds(order); }

            int target = (int)Json.Int(s, "system_index", 0);
            var tr = Json.Obj(s, "transition");
            if (tr != null && Json.Bool(tr, "active"))
            {
                string sig = Json.Int(tr, "target_index") + ":" + Json.Int(tr, "duration_ms");
                if (sig != _lastTransitionSig)
                {
                    _lastTransitionSig = sig;
                    int dur = (int)Json.Int(tr, "duration_ms", GameConstants.GalaxyMapDurationMs, 0, int.MaxValue);
                    Background.StartSynchronizedTransition((int)Json.Int(tr, "target_index"), (int)Json.Int(tr, "elapsed_ms"), dur == 0 ? GameConstants.GalaxyMapDurationMs : dur);
                }
            }
            else if (Background.SystemIndex != target) { Background.SyncToSystemIndex(target); _lastTransitionSig = null; }

            var players = Json.Arr(s, "players");
            var seen = new HashSet<string>();
            if (players != null)
                foreach (var o in players)
                {
                    if (!(o is Dictionary<string, object> d)) continue;
                    string id = Json.Str(d, "id"); if (id.Length == 0) continue;
                    seen.Add(id);
                    if (!Players.TryGetValue(id, out var v)) { v = new DuelViewPlayer { Id = id }; Players[id] = v; PlayerOrder.Add(id); }
                    v.Name = Json.Str(d, "name", "Spieler"); v.Ship = Json.Str(d, "ship", "xwing"); v.Role = Json.Str(d, "role", "bottom");
                    v.Width = (int)Json.Int(d, "width", 80, 1, 2000); v.Height = (int)Json.Int(d, "height", 80, 1, 2000);
                    v.Score = (int)Json.Int(d, "score", 0, 0, int.MaxValue); v.Lives = (int)Json.Int(d, "lives", 0, 0, 99);
                    v.Alive = Json.Bool(d, "alive", true); v.Eliminated = Json.Bool(d, "eliminated"); v.Invulnerable = Json.Bool(d, "invulnerable");
                    v.Kills = (int)Json.Int(d, "kills"); v.Hits = (int)Json.Int(d, "hits"); v.Shots = (int)Json.Int(d, "shots"); v.Damage = (int)Json.Int(d, "damage"); v.SurvivalMs = (int)Json.Int(d, "survival_ms");
                    v.SetTarget(Json.Num(d, "x"), Json.Num(d, "y"));
                }
            foreach (var id in new List<string>(Players.Keys)) if (!seen.Contains(id)) { Players.Remove(id); PlayerOrder.Remove(id); }

            var ast = new List<ViewAsteroid>();
            var al = Json.Arr(s, "asteroids");
            if (al != null) foreach (var o in al) if (o is Dictionary<string, object> d)
                ast.Add(new ViewAsteroid { Id = Json.Str(d, "id"), X = Json.Num(d, "x"), Y = Json.Num(d, "y"), Width = (int)Json.Int(d, "width", 1, 1, 4000), Height = (int)Json.Int(d, "height", 1, 1, 4000), Scale = Json.Num(d, "scale", 1), Frame = (int)Json.Int(d, "frame", 0, 0, 1000) });
            Asteroids = ast;

            var prj = new List<ViewProjectile>();
            var pl = Json.Arr(s, "projectiles");
            if (pl != null) foreach (var o in pl) if (o is Dictionary<string, object> d)
                prj.Add(new ViewProjectile { Id = Json.Str(d, "id"), OwnerId = Json.Str(d, "owner_id"), Weapon = Json.Str(d, "weapon", "laser"), X = Json.Num(d, "x"), Y = Json.Num(d, "y"), Width = (int)Json.Int(d, "width", 1, 1, 500), Height = (int)Json.Int(d, "height", 1, 1, 500) });
            Projectiles = prj;

            var el = Json.Arr(s, "effects");
            if (el != null) foreach (var o in el) if (o is Dictionary<string, object> d)
            {
                string id = Json.Str(d, "id"); if (id.Length == 0 || Effects.ContainsKey(id)) continue;
                Effects[id] = new ViewEffect { Id = id, X = Json.Num(d, "x"), Y = Json.Num(d, "y"), Scale = Json.Num(d, "scale", 0.8), AgeMs = (int)Json.Int(d, "age_ms"), SeenAtMs = Clock.NowMs };
            }

            if (Json.Bool(s, "match_over") && !MatchOver) { MatchOver = true; Result = Json.Obj(s, "result"); ResultStartedMs = Clock.NowMs; }
        }

        private static bool SameList(List<string> a, List<string> b)
        {
            if (a.Count != b.Count) return false;
            for (int i = 0; i < a.Count; i++) if (a[i] != b[i]) return false;
            return true;
        }
    }

    /// <summary>Host-Seite: simuliert autoritativ (PvpWorld), nimmt Client-Eingaben vom LanServer entgegen und sendet Snapshots (alle 50 ms).</summary>
    public sealed class PvpHostDriver
    {
        public readonly PvpWorld World;
        private readonly MultiplayerSession _session;
        private DateTime _lastSnapshot = DateTime.MinValue;
        public bool Quit { get; private set; }
        public long SnapshotsSent { get; private set; }

        public PvpHostDriver(MultiplayerSession session, string requestedMode, ISimRandom rng = null)
        {
            _session = session;
            var infos = new List<PvpPlayerInfo>();
            string hostId = session.HostId;
            var ids = new List<string>(session.Client.PlayerOrder);
            ids.Sort((a, b) => a == hostId ? -1 : (b == hostId ? 1 : string.CompareOrdinal(a, b)));
            string rule = null;
            foreach (var id in ids)
            {
                var d = session.Players[id];
                infos.Add(new PvpPlayerInfo(id, Json.Str(d, "name", "Spieler"), Json.Str(d, "ship", "xwing")));
                if (id == hostId) rule = Json.Str(d, "game_rule", "");
            }
            World = new PvpWorld(PvpModes.IsValid(rule) ? rule : requestedMode, infos, rng);
        }

        public void Step(PlayerInput local)
        {
            foreach (var ev in _session.Poll()) if (Json.Str(ev, "type") == Msg.ServerStopped) Quit = true;
            string localId = _session.LocalId;
            var inputs = new Dictionary<string, PlayerInput>();
            if (_session.Server != null)
            {
                _session.Server.ConsumePvpInputs(out var moves, out var fires);
                foreach (var kv in moves) inputs[kv.Key] = new PlayerInput { Left = kv.Value[0], Right = kv.Value[1] };
                foreach (var f in fires)
                {
                    inputs.TryGetValue(f.Key, out var pi);
                    if (f.Value == "laser") pi.Laser = true; else pi.Torpedo = true;
                    inputs[f.Key] = pi;
                }
            }
            inputs[localId] = local;   // Host nutzt seine lokale Eingabe direkt (kein Netzwerk-Umweg)

            var connected = new HashSet<string>(_session.Players.Keys);
            foreach (var p in World.Players) if (p.Id != localId && !connected.Contains(p.Id)) World.MarkDisconnected(p.Id);

            World.Step(inputs);
            if ((DateTime.UtcNow - _lastSnapshot).TotalMilliseconds >= GameConstants.PvpSnapshotIntervalMs && _session.Server != null)
            {
                _lastSnapshot = DateTime.UtcNow;
                _session.Server.BroadcastPvpSnapshot(World.BuildSnapshot());
                SnapshotsSent++;
            }
        }
    }

    /// <summary>Client-Seite: sendet Eingaben (alle 50 ms) und Schussereignisse, rendert ausschließlich Host-Snapshots.</summary>
    public sealed class PvpClientDriver
    {
        public readonly PvpClientView View;
        private readonly MultiplayerSession _session;
        private DateTime _lastInput = DateTime.MinValue;
        private long _fireSeq;
        public bool Quit { get; private set; }

        public PvpClientDriver(MultiplayerSession session, ISimRandom rng = null) { _session = session; View = new PvpClientView(rng); }

        public void Step(PlayerInput local)
        {
            if (!View.MatchOver)
            {
                if ((DateTime.UtcNow - _lastInput).TotalMilliseconds >= GameConstants.PvpInputIntervalMs)
                { _lastInput = DateTime.UtcNow; _session.Client.SendPvpInput(local.Left, local.Right); }
                if (local.Laser) _session.Client.SendPvpFire("laser", ++_fireSeq);
                if (local.Torpedo) _session.Client.SendPvpFire("torpedo", ++_fireSeq);
            }
            Dictionary<string, object> latest = null;
            foreach (var ev in _session.Poll())
            {
                string t = Json.Str(ev, "type");
                if (t == Msg.PvpSnapshot) latest = ev;
                else if (t == Msg.ServerStopped) { Quit = true; View.HostStopped = true; View.MatchOver = true; View.Result = new Dictionary<string, object> { { "host_stopped", true } }; }
            }
            if (latest != null) View.ApplySnapshot(latest);
            View.Tick();
        }
    }
}
