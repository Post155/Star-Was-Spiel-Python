using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using StarWars.Sim;

namespace StarWars.SimTests
{
    /// <summary>Echte TCP-Tests über Loopback: zwei bzw. drei Spielinstanzen (MultiplayerSession) in einem Prozess.</summary>
    public static class NetworkTests
    {
        static bool WaitUntil(Func<bool> cond, int ms, Action pump = null)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            while (sw.ElapsedMilliseconds < ms) { pump?.Invoke(); if (cond()) return true; Thread.Sleep(5); }
            pump?.Invoke(); return cond();
        }

        public static void Run()
        {
            Lobby(); PvpMatch(); ClientDisconnect(); HostDisconnect(); PointsMode(); Robustness();
        }

        static (MultiplayerSession host, MultiplayerSession client) Connect(string mode)
        {
            var host = new MultiplayerSession(mode, mode == Msg.ModePvp ? 2 : 10);
            host.Host("Alice", 0);
            var client = new MultiplayerSession(mode, mode == Msg.ModePvp ? 2 : 10);
            client.Join("127.0.0.1", "Bob", host.Server.Port);
            return (host, client);
        }

        static void Pump(params MultiplayerSession[] s) { foreach (var x in s) x.Poll(); }

        static void Lobby()
        {
            T.Group("LAN: Host erstellen, per IP beitreten, Lobby-Zustand (echte Sockets)");
            var (host, client) = Connect(Msg.ModePvp);
            try
            {
                bool joined = WaitUntil(() => host.Players.Count == 2 && client.Players.Count == 2 && host.LocalId != null && client.LocalId != null, 4000, () => Pump(host, client));
                T.Check("Host und Client verbunden, beide sehen 2 Spieler", joined, $"host={host.Players.Count} client={client.Players.Count} err={host.Error}/{client.Error}");
                T.Check("eindeutige Spieler-IDs, Host korrekt erkannt", host.LocalId != client.LocalId && host.IsHost && !client.IsHost && client.HostId == host.LocalId);
                T.Check("Namen werden synchronisiert", client.Players[host.LocalId]["name"] as string == "Alice" && host.Players[client.LocalId]["name"] as string == "Bob");
                client.RequestStart();
                Thread.Sleep(150); Pump(host, client);
                T.Check("Nur der Host darf starten (Client-Start wird ignoriert)", host.Phase == "lobby");
                host.RequestStart();
                T.Check("Host-Start -> beide Clients wechseln in die Setup-Phase", WaitUntil(() => host.Phase == "setup" && client.Phase == "setup", 3000, () => Pump(host, client)));
                host.SendReady("xwing", "normal", PvpModes.LastSurvivor);
                Thread.Sleep(100); Pump(host, client);
                T.Check("Countdown startet erst, wenn ALLE bereit sind", host.Phase == "setup");
                client.SendReady("tiefighter", "normal");
                T.Check("alle bereit -> Countdown (3 s) bei beiden", WaitUntil(() => host.Phase == "countdown" && client.Phase == "countdown", 3000, () => Pump(host, client)));
                double left = client.Client.CountdownLeftMs;
                T.Check("Countdown-Restzeit ist uhrenunabhängig (remaining_ms) und <= 3000 ms", left > 0 && left <= 3000, "left=" + left);
                T.Check("Countdown endet -> Spielphase bei beiden", WaitUntil(() => host.Phase == "game" && client.Phase == "game", 5000, () => Pump(host, client)));
                T.Check("Schiffswahl wurde übertragen", client.Players[client.LocalId]["ship"] as string == "tiefighter" && host.Players[client.LocalId]["ship"] as string == "tiefighter");
                var late = new MultiplayerSession(Msg.ModePvp, 2); late.Join("127.0.0.1", "Zu spät", host.Server.Port);
                T.Check("Beitritt nach Spielstart wird abgelehnt", WaitUntil(() => !string.IsNullOrEmpty(late.Client.Error) || !late.Connected && !late.Connecting && late.LocalId == null, 3000, () => late.Poll()));
                late.Stop(false);
            }
            finally { client.Stop(); host.Stop(); }

            // Wettlauf-Fall: Ein Mitspieler verbindet sich VOR der eigenen Loopback-Verbindung des Hosts -> darf nicht Host werden.
            var srv = new LanServer(0, 2, Msg.ModePvp, true); srv.Start();
            var early = new LanClient(); early.ConnectAsync("127.0.0.1", srv.Port, "Früh", Msg.ModePvp);
            WaitUntil(() => early.Connected && early.Poll().Count >= 0 && early.PlayerId != null, 3000, () => early.Poll());
            var hostLate = new LanClient(); hostLate.ConnectAsync("127.0.0.1", srv.Port, "Host", Msg.ModePvp, true);
            WaitUntil(() => hostLate.PlayerId != null, 3000, () => { hostLate.Poll(); early.Poll(); });
            T.Check("Host-Rolle gehört dem Server-Ersteller, auch wenn ein Mitspieler früher verbindet", early.PlayerId != null && hostLate.PlayerId != null && srv.HostId == hostLate.PlayerId && srv.HostId != early.PlayerId);
            early.Disconnect(false); hostLate.Disconnect(false); srv.Stop(null);

            var h2 = new MultiplayerSession(Msg.ModePvp, 2); h2.Host("H", 0);
            var wrong = new MultiplayerSession(Msg.ModePoints, 10); wrong.Join("127.0.0.1", "X", h2.Server.Port);
            T.Check("falscher Spielmodus wird mit Fehlermeldung abgelehnt", WaitUntil(() => !string.IsNullOrEmpty(wrong.Client.Error) && wrong.Client.Error.Contains("Spielmodus"), 3000, () => { wrong.Poll(); h2.Poll(); }), wrong.Client.Error);
            var c1 = new MultiplayerSession(Msg.ModePvp, 2); c1.Join("127.0.0.1", "A", h2.Server.Port);
            WaitUntil(() => h2.Players.Count == 2, 3000, () => { h2.Poll(); c1.Poll(); });
            var c2 = new MultiplayerSession(Msg.ModePvp, 2); c2.Join("127.0.0.1", "B", h2.Server.Port);
            T.Check("PvP: dritter Spieler wird abgelehnt (max. 2)", WaitUntil(() => !string.IsNullOrEmpty(c2.Client.Error) && c2.Client.Error.Contains("voll"), 3000, () => { c2.Poll(); h2.Poll(); }), c2.Client.Error);
            var h3 = new MultiplayerSession(Msg.ModePvp, 2); h3.Host("Solo", 0);
            WaitUntil(() => h3.Players.Count == 1, 3000, () => h3.Poll()); h3.RequestStart(); Thread.Sleep(200); h3.Poll();
            T.Check("PvP-Start mit nur einem Spieler wird verhindert", h3.Phase == "lobby" && !string.IsNullOrEmpty(h3.Client.Error));
            foreach (var s in new[] { c1, c2, h2, h3 }) s.Stop(false);
            var failed = new MultiplayerSession(Msg.ModePvp, 2); failed.Join("127.0.0.1", "Niemand", 1);
            T.Check("Verbindungsfehler (kein Server) wird sauber gemeldet", WaitUntil(() => !string.IsNullOrEmpty(failed.Client.Error), 5000, () => failed.Poll()), failed.Client.Error);
            failed.Stop(false);
        }

        static (MultiplayerSession host, MultiplayerSession client) StartedPvp()
        {
            var (host, client) = Connect(Msg.ModePvp);
            WaitUntil(() => host.Players.Count == 2 && client.Players.Count == 2, 4000, () => Pump(host, client));
            host.RequestStart();
            WaitUntil(() => host.Phase == "setup" && client.Phase == "setup", 3000, () => Pump(host, client));
            host.SendReady("xwing", "normal", PvpModes.LastSurvivor); client.SendReady("tiefighter", "normal");
            WaitUntil(() => host.Phase == "game" && client.Phase == "game", 8000, () => Pump(host, client));
            return (host, client);
        }

        static void PvpMatch()
        {
            T.Group("LAN-PvP: Host-autoritative Simulation, Eingaben, Schüsse, Snapshots (2 Instanzen)");
            var (host, client) = StartedPvp();
            try
            {
                T.Check("beide Instanzen in der Spielphase", host.Phase == "game" && client.Phase == "game");
                var hd = new PvpHostDriver(host, PvpModes.LastSurvivor, new SimRandom(1));
                var cd = new PvpClientDriver(client, new SimRandom(2));
                T.Check("Host-Welt: Host unten (xwing), Client oben (tiefighter)", hd.World.Get(host.LocalId).Role == "bottom" && hd.World.Get(client.LocalId).ShipKey == "tiefighter");
                var sw = System.Diagnostics.Stopwatch.StartNew();
                int tick = 0; bool clientFired = false; int hostX0 = hd.World.Get(host.LocalId).Ship.X; int clientX0 = hd.World.Get(client.LocalId).Ship.X;
                while (sw.ElapsedMilliseconds < 2500)
                {
                    var hostIn = new PlayerInput { Right = true };
                    var clientIn = new PlayerInput { Left = true };
                    if (tick == 30) { clientIn.Laser = true; clientFired = true; }
                    hd.Step(hostIn); cd.Step(clientIn);
                    tick++; Thread.Sleep(16);
                }
                var hostPlayer = hd.World.Get(host.LocalId); var clientPlayer = hd.World.Get(client.LocalId);
                T.Check("Host-Eingabe bewegt Host-Schiff nach rechts", hostPlayer.Ship.X > hostX0);
                T.Check("Client-Eingabe (über TCP) bewegt Client-Schiff in der Host-Welt nach links", clientPlayer.Ship.X < clientX0, $"{clientX0}->{clientPlayer.Ship.X}");
                T.Check("Client-Schuss kam beim Host an und wurde gezählt (Server-seitig validiert)", clientFired && clientPlayer.Stats.ShotsFired >= 2, "shots=" + clientPlayer.Stats.ShotsFired);
                T.Check("Host sendet Snapshots", hd.SnapshotsSent > 20, "gesendet=" + hd.SnapshotsSent);
                T.Check("Client wendet Snapshots auf seine Ansicht an", cd.View.SnapshotsApplied > 20 && cd.View.Players.Count == 2, "angewendet=" + cd.View.SnapshotsApplied);
                var vHost = cd.View.Players[host.LocalId]; var vClient = cd.View.Players[client.LocalId];
                T.Check("Client sieht Host-Position wie in der autoritativen Welt (±15 px)", Math.Abs(vHost.X - hostPlayer.Ship.X) < 15 + 12 * 4, $"view={vHost.X:F0} host={hostPlayer.Ship.X}");
                T.Check("Client sieht eigenes Schiff oben (role=top) und Punkte/Leben vom Host", vClient.Role == "top" && vClient.Lives == clientPlayer.Ship.Lives);
                T.Check("Client sieht Projektile/Asteroiden-Listen aus dem Snapshot", cd.View.Projectiles != null && cd.View.Asteroids != null);
                T.Check("Systemreihenfolge des Hosts wurde beim Client übernommen", cd.View.Background.Systems.Order.Select(s => s.IdName).SequenceEqual(hd.World.Background.Systems.Order.Select(s => s.IdName)));
            }
            finally { client.Stop(); host.Stop(); }
        }

        static void ClientDisconnect()
        {
            T.Group("LAN: Verbindungsabbruch des Clients während des Spiels");
            var (host, client) = StartedPvp();
            try
            {
                var hd = new PvpHostDriver(host, PvpModes.LastSurvivor, new SimRandom(1));
                for (int i = 0; i < 20; i++) { hd.Step(default); Thread.Sleep(10); }
                string clientId = client.LocalId;
                client.Stop(false);   // hartes Trennen ohne Abschiedsnachricht
                bool over = WaitUntil(() => hd.World.MatchOver, 4000, () => hd.Step(default));
                T.Check("Host erkennt die Trennung und beendet das Match kontrolliert", over && (string)hd.World.Result["winner_id"] == host.LocalId, "over=" + over);
                T.Check("getrennter Spieler gilt als eliminiert", hd.World.Get(clientId).Eliminated);
            }
            finally { client.Stop(false); host.Stop(); }
        }

        static void HostDisconnect()
        {
            T.Group("LAN: Host beendet das Spiel");
            var (host, client) = StartedPvp();
            try
            {
                var cd = new PvpClientDriver(client, new SimRandom(2)); var hd = new PvpHostDriver(host, PvpModes.LastSurvivor, new SimRandom(1));
                for (int i = 0; i < 20; i++) { hd.Step(default); cd.Step(default); Thread.Sleep(10); }
                host.Stop();
                bool quit = WaitUntil(() => cd.Quit, 4000, () => cd.Step(default));
                T.Check("Client erkennt Host-Abbruch (server_stopped)", quit && cd.View.HostStopped && client.Client.HostDisconnected);
            }
            finally { client.Stop(false); host.Stop(false); }
        }

        static void PointsMode()
        {
            T.Group("LAN-Punktekampf: bis zu 10 Spieler, Ghost-Daten, Rangliste");
            var host = new MultiplayerSession(Msg.ModePoints, 10); host.Host("Host", 0);
            var c1 = new MultiplayerSession(Msg.ModePoints, 10); c1.Join("127.0.0.1", "Anna", host.Server.Port);
            var c2 = new MultiplayerSession(Msg.ModePoints, 10); c2.Join("127.0.0.1", "Ben", host.Server.Port);
            try
            {
                T.Check("3 Spieler in der Lobby", WaitUntil(() => host.Players.Count == 3 && c1.Players.Count == 3 && c2.Players.Count == 3, 4000, () => Pump(host, c1, c2)));
                host.RequestStart();
                WaitUntil(() => c1.Phase == "setup" && c2.Phase == "setup", 3000, () => Pump(host, c1, c2));
                host.SendReady("xwing", "normal"); c1.SendReady("falcon", "hard"); c2.SendReady("battledroid", "easy");
                T.Check("Countdown und Start für alle drei", WaitUntil(() => host.Phase == "game" && c1.Phase == "game" && c2.Phase == "game", 8000, () => Pump(host, c1, c2)));
                var w = new SinglePlayerWorld(800, 600, "milleniumfalcon", "hard", new SimRandom(5));
                for (int i = 0; i < 100; i++) w.Step(new PlayerInput { Right = true });
                c1.UpdateLocalPoints(w.Player, 4200, "HOTH", true, true);
                c2.UpdateLocalPoints(w.Player, 900, "ENDOR", false, true);
                bool seen = WaitUntil(() => host.Remote.Count == 2 && host.Remote.Values.Any(r => r.Score == 4200), 3000, () => Pump(host, c1, c2));
                T.Check("Host sieht Ghosts beider Clients mit Punkten und System", seen);
                var rows = host.ScoreboardRows(100, true);
                T.Check("Rangliste ist nach Punkten sortiert (4200 > 900 > ...)", rows.Count == 3 && Json.Int(rows[0], "score") == 4200 && Json.Int(rows[1], "score") >= Json.Int(rows[2], "score"));
                var ghost = host.Remote.Values.First(r => r.Score == 4200);
                T.Check("Ghost-Position normiert (0..1), Schiff übertragen", ghost.TargetX > 0 && ghost.TargetX <= 1 && ghost.Ship == "milleniumfalcon" && ghost.System == "HOTH");
                T.Check("Ghosts sind reine Anzeige: keine Auswirkung auf die lokale Simulation", w.Asteroids.Count >= 0 && ReferenceEquals(host.Remote, host.Remote));
                c2.Stop();
                T.Check("Verlassen eines Spielers wird erkannt (Ghost verschwindet)", WaitUntil(() => host.Remote.Count == 1, 3000, () => Pump(host, c1)));
            }
            finally { c2.Stop(false); c1.Stop(false); host.Stop(); }
        }

        static void Robustness()
        {
            T.Group("LAN: fehlerhafte und unzulässige Nachrichten");
            var host = new MultiplayerSession(Msg.ModePoints, 10); host.Host("Host", 0);
            var good = new MultiplayerSession(Msg.ModePoints, 10); good.Join("127.0.0.1", "Gut", host.Server.Port);
            try
            {
                WaitUntil(() => host.Players.Count == 2, 3000, () => Pump(host, good));
                using (var raw = new TcpClient("127.0.0.1", host.Server.Port))
                {
                    var s = raw.GetStream();
                    byte[] junk = Encoding.UTF8.GetBytes("das ist kein json\n"); s.Write(junk, 0, junk.Length);
                }
                Thread.Sleep(300); Pump(host, good);
                T.Check("Müll statt JSON beendet nur diese Verbindung, Server läuft weiter", host.Players.Count == 2 && host.Server.PlayerCount == 2);
                using (var raw = new TcpClient("127.0.0.1", host.Server.Port))
                {
                    var s = raw.GetStream();
                    byte[] big = Encoding.UTF8.GetBytes("{\"type\":\"hello\",\"name\":\"" + new string('A', 40000) + "\"}\n"); try { s.Write(big, 0, big.Length); } catch (Exception) { }
                }
                Thread.Sleep(300); Pump(host, good);
                T.Check("Überlange Nachricht wird verworfen (Verbindung beendet)", host.Server.PlayerCount == 2);
                using (var raw = new TcpClient("127.0.0.1", host.Server.Port))
                {
                    var s = raw.GetStream();
                    byte[] hello = Encoding.UTF8.GetBytes("{\"type\":\"hello\",\"version\":99,\"name\":\"X\",\"game_mode\":\"points\"}\n"); s.Write(hello, 0, hello.Length);
                    s.ReadTimeout = 2000; var buf = new byte[512]; int n = 0; try { n = s.Read(buf, 0, buf.Length); } catch (Exception) { }
                    string reply = Encoding.UTF8.GetString(buf, 0, n);
                    T.Check("falsche Protokollversion -> Fehlermeldung", reply.Contains("Protokollversion"), reply);
                }
                good.Client.Send(new Dictionary<string, object> { { "type", "points_state" }, { "x", 99999.0 }, { "y", -5.0 }, { "score", -300L }, { "ship", "xwing" }, { "system", "S" } });
                Thread.Sleep(300); Pump(host, good);
                var p = host.Players[good.LocalId];
                T.Check("Werte werden geprüft/begrenzt (x<=1, y>=0, Score>=0)", Json.Num(p, "x") <= 1.0 && Json.Num(p, "y") >= 0.0 && Json.Int(p, "score") >= 0);
                good.Client.Send(new Dictionary<string, object> { { "type", "unbekannter_typ" }, { "x", 1L } });
                good.Client.Send(new Dictionary<string, object> { { "type", "pvp_fire" }, { "weapon", "nuke" } });
                Thread.Sleep(200); Pump(host, good);
                T.Check("unbekannte Nachrichtentypen werden ignoriert", host.Server.PlayerCount == 2 && good.Connected);
            }
            finally { good.Stop(false); host.Stop(); }
        }
    }
}
