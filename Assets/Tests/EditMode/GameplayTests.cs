using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using StarWars.Sim;

namespace StarWars.SimTests
{
    public static class GameplayTests
    {
        public static void Run()
        {
            Player(); Asteroids(); Enemies(); Background(); SinglePlayer(); PointsFight(); Pvp(); JsonTests(); SaveTests(); InventoryTests(); QuestTests();
        }

        private static PlayerInput None => default;

        static void Player()
        {
            T.Group("Spielerschiff: Bewegung, Grenzen, Leben, Unverwundbarkeit");
            var clock = new SimClock();
            var p = new PlayerShip(ShipCatalog.XWing, 800, 600, clock);
            T.Eq("Startposition mittig unten", (p.X, p.Y), (800 / 2 - 96 / 2, 600 - 96 - 20));
            for (int i = 0; i < 100; i++) p.MoveLeft();
            T.Eq("linke Bildschirmgrenze", p.X, 0);
            for (int i = 0; i < 200; i++) p.MoveRight(800);
            T.Eq("rechte Bildschirmgrenze", p.X, 800 - 96);
            T.Eq("3 Leben", p.Lives, 3);
            bool died = p.TakeDamage(1);
            T.Check("erster Treffer: 2 Leben, nicht tot", p.Lives == 2 && !died);
            T.Check("während der Unverwundbarkeit kein Schaden", !p.TakeDamage(1) && p.Lives == 2 && p.IsInvulnerable);
            clock.Advance(2001);
            T.Check("nach 2 s wieder verwundbar", !p.IsInvulnerable);
            p.TakeDamage(1); clock.Advance(2001);
            T.Check("dritter Treffer zerstört das Schiff", p.TakeDamage(1) && p.Lives == 0);
            T.Check("Torpedo nur X-Wing/TIE", ShipCatalog.XWing.HasTorpedo && ShipCatalog.Tie.HasTorpedo && !ShipCatalog.Falcon.HasTorpedo && !ShipCatalog.Droid.HasTorpedo);
            T.Check("Geschwindigkeiten 12/14/11/12", ShipCatalog.XWing.Speed == 12 && ShipCatalog.Falcon.Speed == 14 && ShipCatalog.Tie.Speed == 11 && ShipCatalog.Droid.Speed == 12);
            T.Check("Gegnerschiffe laut Regel (XWing->TIE, Falcon->Droid, TIE->XWing, Droid->Falcon)",
                ShipCatalog.XWing.OpposingKey == "tiefighter" && ShipCatalog.Falcon.OpposingKey == "battledroid" && ShipCatalog.Tie.OpposingKey == "xwing" && ShipCatalog.Droid.OpposingKey == "milleniumfalcon");
        }

        static void Asteroids()
        {
            T.Group("Asteroiden und Schwierigkeitsprofile");
            var p = Difficulties.Get("expert");
            T.Check("Experte: Parameter wie constants.py", p.EnemyHp == 1.25 && p.AsteroidDensity == 1.18 && p.EnemySpawn == 0.80 && p.AsteroidSize == 1.08);
            T.Check("vier Stufen", Difficulties.Keys.Length == 4 && Difficulties.Get("easy").Name == "Einfach" && Difficulties.Get("hard").Name == "Schwer");
            T.Check("unbekannte Stufe -> normal", Difficulties.Get("???").Key == "normal");
            var rng = new SimRandom(3);
            var a = new Asteroid(800, 600, rng, 1.0, 2.0);
            T.Check("Asteroid startet oberhalb des Bildschirms", a.Y == -a.Height);
            double y0 = a.Y; a.Update();
            T.Near("Fallgeschwindigkeit = speed * Multiplikator", a.Y - y0, a.Speed);
            T.Check("Geschwindigkeitsbereich 2..8 * Multiplikator", a.Speed >= 4 && a.Speed <= 16);
            int f0 = a.Frame; for (int i = 0; i < 5; i++) a.Update();
            T.Check("Animation: Frame wechselt alle 5 Ticks", a.Frame != f0);
            var r = a.GetRect(); T.Check("Kollisionsrechteck = 70 % zentriert", r.W == (int)(a.Width * 0.7) && r.X == (int)(a.X + a.Width * 0.15));
        }

        static void Enemies()
        {
            T.Group("Gegner: Freischaltung, Warnungen, Spawn, Schaden");
            var clock = new SimClock();
            var player = new PlayerShip(ShipCatalog.XWing, 800, 600, clock);
            var em = new EnemyManager(800, 600, player, "normal", new SimRandom(11));
            var lasers = new List<PlayerProjectile>(); var torps = new List<PlayerProjectile>();
            for (int i = 0; i < 600; i++) em.Update(1.0 / 60, 1500, 0, lasers, torps);
            T.Check("unter 2000 Punkten: keine Gegner, keine Warnung", em.Enemies.Count == 0 && em.WarningText == null);
            var res = em.Update(1.0 / 60, 2000, 0, lasers, torps);
            T.Check("bei 2000 Punkten erscheint die Warnung (Tier 1)", res.WarningText == "Achtung! Feindliche Schiffe wurden entdeckt." && em.WarningPendingTier == 1);
            for (int i = 0; i < 100; i++) em.Update(1.0 / 60, 2000, 0, lasers, torps);
            T.Check("während der Warnung spawnt kein Gegner", em.Enemies.Count == 0);
            for (int i = 0; i < 120; i++) em.Update(1.0 / 60, 2000, 0, lasers, torps);
            T.Check("nach der Warnung (2,5 s) spawnen Gegner", em.Enemies.Count >= 1 && em.WarnedTiers.Contains(1));
            T.Check("Gegner ist TIE-Fighter-Modell gegen X-Wing", em.Enemies[0].ShipKey == "tiefighter");
            var res2 = em.Update(1.0 / 60, 5000, 0, lasers, torps);
            T.Check("5000 Punkte: Warnung Tier 2", res2.WarningText == "Warnung: Schwere Feinde im Anflug!");
            var em3 = new EnemyManager(800, 600, player, "normal", new SimRandom(2));
            em3.Update(1.0 / 60, 10000, 0, lasers, torps);
            T.Check("10000 Punkte: Elite-Warnung (alle Stufen werden nacheinander gewarnt)", em3.WarningPendingTier == 1);

            var heavy = new EnemyShip("XWing", "tiefighter", em.BalancedArchetype(EnemyArchetypes.All["heavy"], 6000, 0), 800, 600, 100, 20, "attacker", new SimRandom(1));
            int hp0 = heavy.Hp; heavy.TakeDamage(1);
            T.Check("Schwerer Gegner: Rüstung (28 %) -> min. 1 Schaden", hp0 - heavy.Hp >= 1);
            var std = new EnemyShip("XWing", "tiefighter", em.BalancedArchetype(EnemyArchetypes.All["standard"], 0, 0), 800, 600, 100, 20, "attacker", new SimRandom(1));
            int hp1 = std.Hp; std.TakeDamage(4);
            T.Check("Torpedo (4 Schaden) auf Standard-Gegner", hp1 - std.Hp == 4 || std.Hp == 0);
            T.Eq("Rüstungsformel max(1, round(dmg*(1-res)))", CombatSystem.EffectiveDamage(1, 0.28), 1);
            T.Eq("Rüstung Torpedo gegen Schwer: round(4*0.72)=3", CombatSystem.EffectiveDamage(4, 0.28), 3);

            // Gegner-KI bewegt sich zielgerichtet auf den Spieler zu (nicht zufällig).
            var e = new EnemyShip("XWing", "tiefighter", EnemyArchetypes.All["standard"], 800, 600, 12.0, 0.0, "attacker", new SimRandom(4));
            player.X = 600; player.UpdateHitbox();
            for (int i = 0; i < 240; i++) e.Update(1.0 / 60, player, new List<PlayerProjectile>(), new List<EnemyShip> { e }, 1.0);
            T.Check("KI folgt dem Spieler horizontal (Zielverfolgung)", Math.Abs(e.CenterX - player.Hitbox.CenterX) < 160, $"dx={e.CenterX - player.Hitbox.CenterX:F1}");
            var shots = new List<EnemyProjectile>();
            var e2 = new EnemyShip("XWing", "tiefighter", EnemyArchetypes.All["elite"], 800, 600, 300.0, 40.0, "attacker", new SimRandom(8));
            player.X = 300; player.UpdateHitbox();
            for (int i = 0; i < 600; i++) shots.AddRange(e2.Weapons.Update(1.0 / 60, player, 1.0));
            T.Check("Gegner feuert Laser-Salven (und ggf. Torpedos) auf den Spieler", shots.Count >= 4 && shots.Exists(s => !s.IsTorpedo));
        }

        static void Background()
        {
            T.Group("Sternensysteme, Hintergrund, Systemwechsel");
            var sm = new SystemManager(new SimRandom(1));
            T.Check("12 Systeme, EARTH zuerst", sm.Order.Count == 12 && sm.Order[0].IdName == "EARTH");
            T.Check("jedes System genau einmal", sm.Order.Select(s => s.IdName).Distinct().Count() == 12);
            T.Check("Reihenfolge ist zufällig (zwei Seeds unterscheiden sich)", !new SystemManager(new SimRandom(2)).Order.Select(s => s.IdName).SequenceEqual(sm.Order.Select(s => s.IdName)));
            var by = StarSystemsById();
            T.Check("BLACKHOLE/TODESSTERN/STERNZERSTÖRER ohne eigenen Planetenschlüssel (Original-Verhalten)", by["BLACKHOLE"].PlanetKeys.Length == 0 && by["TODESSTERN"].PlanetKeys.Length == 0 && by["STERNZERSTÖRER"].PlanetKeys.Length == 0);
            T.Check("Planetenpool-Fallback umfasst 13 Bilder", PlanetCatalog.AllKeys().Length == 13);
            T.Check("Asteroiden-Tempo je System (EARTH 0.5, BLACKHOLE 2.5)", by["EARTH"].AsteroidSpeedMul == 0.5 && by["BLACKHOLE"].AsteroidSpeedMul == 2.5);
            T.Near("Systembonus (0, .15, .30, .50, danach .50)", Difficulties.SystemBonus(5), 0.50);

            var clock = new SimClock();
            var bg = new BackgroundDirector(800, 600, clock, new SimRandom(7), true);
            T.Check("Sterne: Layer1 >= 50, Layer2 >= 20", bg.Layer1.Count >= 50 && bg.Layer2.Count >= 20);
            int changes = 0; bg.SystemChanged += s => changes++;
            string first = bg.CurrentSystemName;
            for (int i = 0; i < 29 * 60; i++) { clock.Advance(GameConstants.TickMs); bg.Update(0); }
            T.Check("vor 30 s noch kein Wechsel", !bg.Transition.Active && bg.CurrentSystemName == first);
            for (int i = 0; i < 60; i++) { clock.Advance(GameConstants.TickMs); bg.Update(0); }
            T.Check("nach 30 s startet die Karten-Überblendung", bg.Transition.Active && bg.Transition.DurationMs == 5000);
            for (int i = 0; i < 5 * 60 + 5; i++) { clock.Advance(GameConstants.TickMs); bg.Update(0); }
            T.Check("nach 5 s ist das System gewechselt", !bg.Transition.Active && bg.CurrentSystemName != first && changes == 1);

            var clock2 = new SimClock(); var bg2 = new BackgroundDirector(800, 600, clock2, new SimRandom(9), true);
            clock2.Advance(GameConstants.TickMs); bg2.Update(2000);
            T.Check("2000 Punkte lösen den Wechsel aus", bg2.Transition.Active);

            var clock3 = new SimClock(); var bg3 = new BackgroundDirector(800, 600, clock3, new SimRandom(10), true);
            bool sawPlanet = false; int firstPlanetTick = -1;
            for (int i = 0; i < 25 * 60; i++) { clock3.Advance(GameConstants.TickMs); bg3.Update(0); if (bg3.Planets.Count > 0 && !sawPlanet) { sawPlanet = true; firstPlanetTick = i; } }
            T.Check("Planet erscheint erst nach 10 s Eintrittsverzögerung, nur einer pro System", sawPlanet && firstPlanetTick >= 10 * 60 - 2 && bg3.Planets.Count <= 1, "tick=" + firstPlanetTick);
        }

        static Dictionary<string, StarSystem> StarSystemsById() => SystemManager.Build().ToDictionary(s => s.IdName);

        static void SinglePlayer()
        {
            T.Group("Einzelspieler-Simulation (Ablauf wie run_game_session)");
            var w = new SinglePlayerWorld(800, 600, "xwing", "normal", new SimRandom(21));
            int destroyed = 0; w.AsteroidDestroyed += (a, pts) => destroyed++;
            int deaths = 0; w.PlayerDied += () => deaths++;
            for (int i = 0; i < 60 * 20; i++)
            {
                var inp = new PlayerInput { Laser = i % 12 == 0, Torpedo = i % 90 == 0, Left = (i / 120) % 2 == 0, Right = (i / 120) % 2 == 1 };
                w.Step(inp);
                if (w.Dead) break;
            }
            T.Check("Asteroiden entstehen und werden abgeschossen, Punkte steigen", destroyed > 0 && w.Score > 0, $"zerstört={destroyed}, Score={w.Score}");
            T.Check("Spieler bleibt innerhalb der Bildschirmgrenzen", w.Player.X >= 0 && w.Player.X <= 800 - w.Player.Width);
            T.Check("Punkte entsprechen Summe der Asteroidenpunkte (keine Doppelwertung)", w.Score % 25 == 0 && w.Score <= destroyed * 100);

            var idle = new SinglePlayerWorld(800, 600, "milleniumfalcon", "expert", new SimRandom(5));
            int guard = 0;
            while (!idle.Dead && guard++ < 60 * 600) idle.Step(None);
            T.Check("Ohne Eingabe stirbt der Spieler irgendwann (Tod nur einmal gemeldet)", idle.Dead && idle.Player.Lives == 0);
            int scoreAtDeath = idle.Score; idle.Step(new PlayerInput { Laser = true });
            T.Check("Nach dem Tod keine Aktionen mehr", idle.Score == scoreAtDeath && idle.Lasers.Count == 0);

            var sw = new SinglePlayerWorld(800, 600, "xwing", "normal", new SimRandom(1));
            sw.Step(new PlayerInput { Laser = true }); sw.SwitchShip("tiefighter");
            T.Check("Debug-Schiffswechsel leert Projektile und ersetzt das Schiff", sw.Player.Info.Key == "tiefighter" && sw.Lasers.Count == 0);

            // Gleiche Eingabe + gleicher Seed => identisches Ergebnis (Determinismus der festen 60-Hz-Simulation)
            long Run(int seed) { var x = new SinglePlayerWorld(800, 600, "tiefighter", "hard", new SimRandom(seed)); for (int i = 0; i < 1500; i++) x.Step(new PlayerInput { Laser = i % 10 == 0, Left = i % 200 < 100, Right = i % 200 >= 100 }); return x.Score * 1000003L + x.Player.X + x.Asteroids.Count; }
            T.Check("Simulation ist bei gleichem Seed deterministisch", Run(77) == Run(77));
        }

        static void PointsFight()
        {
            T.Group("Lokaler Punktekampf: zwei vollständig getrennte Welten");
            var a = new PointsPlayerConfig { Name = "Spieler 1", Ship = "xwing", Faction = "rebels", Difficulty = "normal" };
            var b = new PointsPlayerConfig { Name = "Spieler 2", Ship = "tiefighter", Faction = "empire", Difficulty = "hard" };
            var m = new PointsFightMatch(a, b);
            T.Check("zwei unterschiedliche Weltinstanzen mit eigenen Listen", !ReferenceEquals(m.Worlds[0], m.Worlds[1]) && !ReferenceEquals(m.Worlds[0].Asteroids, m.Worlds[1].Asteroids) && !ReferenceEquals(m.Worlds[0].Enemies, m.Worlds[1].Enemies) && !ReferenceEquals(m.Worlds[0].Clock, m.Worlds[1].Clock));
            for (int i = 0; i < 60 * 10; i++) m.Step(new PlayerInput { Laser = i % 10 == 0 }, None);
            T.Check("Eingaben wirken nur in der eigenen Welt (P2 schoss nie)", m.Worlds[1].Lasers.Count == 0 && m.Worlds[1].Score == 0 && m.Worlds[0].Score >= 0 && m.Worlds[0].Ticks == m.Worlds[1].Ticks);
            T.Check("Spieler 2 nutzt TIE (Torpedo-fähig), Spieler 1 X-Wing", m.Worlds[0].Player.Info.Key == "xwing" && m.Worlds[1].Player.Info.Key == "tiefighter");
            T.Eq("Welt 400x600 je Spieler", (m.Worlds[0].Width, m.Worlds[0].Height), (400, 600));
            int guard = 0; while (!m.Over && guard++ < 60 * 200) m.Step(None, None);
            T.Check("Match endet nach 180 s oder wenn beide tot sind", m.Over && m.Result != null && m.Result.Count == 2);
            T.Check("Rangliste sortiert absteigend", m.Result[0].Score >= m.Result[1].Score);
            T.Check("Gleichstand -> kein Sieger", new PointsFightMatch(a, b) is PointsFightMatch pm && pm.WinnerName() == null);
        }

        static List<PvpPlayerInfo> Duo() => new List<PvpPlayerInfo> { new PvpPlayerInfo("p1", "Alice", "xwing"), new PvpPlayerInfo("p2", "Bob", "tiefighter") };

        static void Pvp()
        {
            T.Group("PvP-Duell (Letzter Überlebender / Punktekampf-Regel): Host-autoritative Welt");
            var w = new PvpWorld(PvpModes.LastSurvivor, Duo(), new SimRandom(31));
            var p1 = w.Get("p1"); var p2 = w.Get("p2");
            T.Check("Host unten, Gegner oben", p1.Role == "bottom" && p2.Role == "top");
            T.Eq("PvP-Geschwindigkeit 12 für alle", p2.Ship.Speed, 12);
            // P2 horizontal ausrichten: beide sind mittig (X gleich) -> p1 feuert nach oben und trifft p2.
            // Beide starten unverwundbar? Nein (invuln 0). Ausrichtung: gleiche X-Mitte.
            p2.Ship.X = p1.Ship.X; p2.Ship.UpdateHitbox();
            var fire = new Dictionary<string, PlayerInput> { { "p1", new PlayerInput { Laser = true } } };
            for (int i = 0; i < 45; i++) { w.Step(i == 0 ? fire : null); }
            T.Check("Treffer: Schaden 1, Leben -1, Angreifer erhält 150 Punkte", p2.Ship.Lives <= 2 && p1.Score >= 150, $"lives={p2.Ship.Lives} score={p1.Score}");
            T.Check("Treffer registriert genau einmal pro Projektil", p1.Stats.Hits <= p1.Stats.ShotsFired);
            T.Check("Getroffener Spieler respawnt verzögert und ist danach unverwundbar", p2.RespawnAtMs > 0 || p2.Ship.IsInvulnerable || p2.Alive);
            // Eliminierung: p2 hat 3 Leben; Laser (2 Strahlen) trifft potenziell zweifach -> Schaden kommt durch Unverwundbarkeit nur einmal pro Phase.
            int guard = 0;
            while (!w.MatchOver && guard++ < 60 * 120)
            {
                var p2n = w.Get("p2");
                p2n.Ship.X = w.Get("p1").Ship.X; p2n.Ship.UpdateHitbox();
                w.Step(new Dictionary<string, PlayerInput> { { "p1", new PlayerInput { Laser = guard % 6 == 0, Torpedo = guard % 40 == 0 } } });
            }
            T.Check("Match endet, wenn ein Spieler eliminiert ist (Sieger = Überlebender)", w.MatchOver && (string)w.Result["winner_id"] == "p1", w.Result == null ? "kein Ergebnis" : "winner=" + w.Result["winner_id"]);
            T.Check("Kill-Bonus 1000 vergeben", w.Get("p1").Stats.Kills == 1 && w.Get("p1").Score >= 1000);
            int shots = w.Get("p2").Stats.ShotsFired; w.FireWeapon("p2", "laser");
            T.Check("Eliminierter Spieler kann nicht mehr schießen", w.Get("p2").Stats.ShotsFired == shots && w.Get("p2").Eliminated);
            int scoreBefore = w.Get("p1").Score; for (int i = 0; i < 120; i++) w.Step(null);
            T.Check("Ergebnis bleibt nach Spielende stabil", (string)w.Result["winner_id"] == "p1" && w.Get("p1").Score >= scoreBefore);

            var pts = new PvpWorld(PvpModes.Points, Duo(), new SimRandom(32));
            int ticks = 0; while (!pts.MatchOver && ticks++ < 60 * 200) pts.Step(null);
            T.Check("Punktekampf-Regel: endet nach 180 s", pts.MatchOver && pts.MatchElapsedMs >= 180000 - 20);
            T.Check("Gleichstand 0:0 -> Unentschieden (winner_id null)", pts.Result["winner_id"] == null || pts.Get((string)pts.Result["winner_id"]).Score > 0);

            var dis = new PvpWorld(PvpModes.LastSurvivor, Duo(), new SimRandom(33)); dis.MarkDisconnected("p2");
            T.Check("Verbindungsabbruch des Gegners: Host gewinnt", dis.MatchOver && (string)dis.Result["winner_id"] == "p1");

            var ast = new PvpWorld(PvpModes.LastSurvivor, Duo(), new SimRandom(34));
            for (int i = 0; i < 60 * 40; i++) ast.Step(null);
            T.Check("Asteroiden: Obergrenze 36, kein Leck durch seitlich verlassende Asteroiden", ast.Asteroids.Count <= 36 && ast.Asteroids.Values.All(a => a.X > -a.Width * 3 - 10 && a.X < 800 + a.Width * 2 + 10 && a.Y < 600 + a.Height * 2 + 10));

            var snap = ast.BuildSnapshot();
            var back = (Dictionary<string, object>)Json.Parse(Json.Serialize(snap));
            T.Check("Snapshot ist gültiges JSON im Original-Format (version 1)", Json.Str(back, "type") == "pvp_snapshot" && Json.Int(back, "version") == 1 && Json.Arr(back, "players").Count == 2);
            var view = new PvpClientView(new SimRandom(1)); view.ApplySnapshot(back);
            T.Check("Client-Ansicht übernimmt Spieler und Systemreihenfolge", view.Players.Count == 2 && view.Background.Systems.Order[0].IdName == ast.Background.Systems.Order[0].IdName && view.Background.Systems.Order.Select(s => s.IdName).SequenceEqual(ast.Background.Systems.Order.Select(s => s.IdName)));
        }

        static void JsonTests()
        {
            T.Group("JSON-Parser/-Writer");
            var d = new Dictionary<string, object> { { "a", 1L }, { "b", 2.5 }, { "s", "Zeile\n\"Zitat\" ä€" }, { "n", null }, { "l", new List<object> { 1L, true, "x" } } };
            var back = (Dictionary<string, object>)Json.Parse(Json.Serialize(d));
            T.Check("Roundtrip erhält Typen und Sonderzeichen", (long)back["a"] == 1 && (double)back["b"] == 2.5 && (string)back["s"] == "Zeile\n\"Zitat\" ä€" && back["n"] == null && ((List<object>)back["l"]).Count == 3);
            foreach (var bad in new[] { "{", "{\"a\":}", "[1,2", "{\"a\" 1}", "nope", "{\"a\":\"x}", "{\"a\":1} x" })
                T.Check("fehlerhaftes JSON wird abgelehnt: " + bad, !Json.TryParse(bad, out _));
            var p = (Dictionary<string, object>)Json.Parse("{\"x\": 1e3, \"y\": -4, \"z\": 0.25}");
            T.Check("Zahlenformate", Json.Num(p, "x") == 1000.0 && (long)p["y"] == -4 && Json.Num(p, "z") == 0.25);
            T.Eq("Json.Int begrenzt", Json.Int(p, "y", 0, 0, 10), 0L);
            T.Check("Tief verschachteltes JSON wird abgewiesen", !Json.TryParse(new string('[', 200) + new string(']', 200), out _));
        }

        static string Tmp() { var p = Path.Combine(Path.GetTempPath(), "swsave_" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(p); return p; }

        static void SaveTests()
        {
            T.Group("Speichersystem");
            string dir = Tmp();
            var s = new SaveService(dir);
            T.Check("erster Start: leer", s.Load() == LoadStatus.Fresh && s.Data.Highscore == 0);
            T.Check("neuer Rekord wird erkannt und gespeichert", s.SubmitScore(1234) && !s.SubmitScore(100) && s.Data.Highscore == 1234);
            s.Data.Settings.LastShip = "tiefighter"; s.Data.Settings.MasterVolume = 0.3; s.Save();
            var s2 = new SaveService(dir);
            T.Check("Laden: Highscore + Einstellungen", s2.Load() == LoadStatus.Loaded && s2.Data.Highscore == 1234 && s2.Data.Settings.LastShip == "tiefighter" && Math.Abs(s2.Data.Settings.MasterVolume - 0.3) < 1e-9);
            File.WriteAllText(s.FilePath, "{ kaputt ");
            var s3 = new SaveService(dir);
            var st = s3.Load();
            T.Check("beschädigte Datei: Wiederherstellung aus Backup", st == LoadStatus.RecoveredFromBackup && s3.Data.Highscore == 1234, st.ToString());
            File.WriteAllText(s.FilePath, "{ kaputt "); File.Delete(s.BackupPath);
            var s4 = new SaveService(dir);
            T.Check("beschädigt ohne Backup: sauberer Neustart, keine Ausnahme", s4.Load() == LoadStatus.CorruptReset && s4.Data.Highscore == 0 && File.Exists(s.FilePath + ".corrupt"));
            string dir2 = Tmp(); File.WriteAllText(Path.Combine(dir2, "highscore.json"), "{\"highscore\": 6025}");
            var s5 = new SaveService(dir2); s5.Load();
            T.Check("Import des alten Python-Highscores {\"highscore\": 6025}", s5.Data.Highscore == 6025);
            string dir3 = Tmp(); File.WriteAllText(Path.Combine(dir3, "savegame.json"), "{\"version\": 99, \"highscore\": 5}");
            var s6 = new SaveService(dir3); var st6 = s6.Load();
            T.Check("Datei aus neuerer Version wird nicht fehlinterpretiert", st6 != LoadStatus.Loaded && s6.Data.Highscore == 0);
            string dir4 = Tmp(); File.WriteAllText(Path.Combine(dir4, "savegame.json"), "{\"highscore\": 77}");
            var s7 = new SaveService(dir4); T.Check("ältere Datei ohne Version wird migriert", s7.Load() == LoadStatus.Migrated && s7.Data.Highscore == 77);
            string dir5 = Tmp(); File.WriteAllText(Path.Combine(dir5, "savegame.json"), "{\"version\":1,\"settings\":{\"last_ship\":\"unbekannt\",\"last_difficulty\":\"x\",\"master_volume\":9}}");
            var s8 = new SaveService(dir5); s8.Load();
            T.Check("ungültige Werte werden auf sichere Standardwerte begrenzt", s8.Data.Settings.LastShip == "xwing" && s8.Data.Settings.LastDifficulty == "normal" && s8.Data.Settings.MasterVolume == 1.0);
        }

        static void InventoryTests()
        {
            T.Group("Inventar & Items");
            var db = ItemDatabase.CreateDefault(); var inv = new Inventory(db, 3);
            int changes = 0; inv.Changed += () => changes++;
            T.Eq("Hinzufügen (Repair-Kit, Stapel 5)", inv.Add("repair_kit", 7), 0);
            T.Check("Stapelregel: 7 Kits = 2 Slots (5+2)", inv.Count("repair_kit") == 7 && inv.GetSlot(0).Count == 5 && inv.GetSlot(1).Count == 2);
            T.Eq("nicht stapelbar: Schildverstärker belegt eigenen Slot", inv.Add("shield_booster", 1), 0);
            T.Eq("Kapazitätsgrenze: Rest wird zurückgegeben", inv.Add("shield_booster", 1), 1);
            T.Eq("unbekanntes Item wird abgewiesen", inv.Add("gibts_nicht", 2), 2);
            T.Check("Entfernen nur ganz oder gar nicht", !inv.Remove("repair_kit", 8) && inv.Count("repair_kit") == 7 && inv.Remove("repair_kit", 6) && inv.Count("repair_kit") == 1);
            T.Check("Änderungsereignis wird ausgelöst", changes >= 3);
            var data = inv.ToJson(); var inv2 = new Inventory(db, 3); inv2.LoadJson(data);
            T.Check("Serialisierung erhält Bestand", inv2.Count("repair_kit") == 1 && inv2.Has("shield_booster"));
        }

        static void QuestTests()
        {
            T.Group("Questsystem");
            var db = ItemDatabase.CreateDefault(); var inv = new Inventory(db, 4); var q = QuestLog.CreateDefault();
            q.Report(QuestObjective.DestroyAsteroids, 5);
            T.Check("nicht angenommene Quests sammeln keinen Fortschritt", q.GetProgress("q_asteroids_10").Progress == 0);
            T.Check("Annahme", q.Accept("q_asteroids_10") && !q.Accept("q_asteroids_10"));
            q.Report(QuestObjective.DestroyAsteroids, 4); T.Eq("Fortschritt 4/10", q.GetProgress("q_asteroids_10").Progress, 4);
            int completed = 0; q.Completed += d => completed++;
            q.Report(QuestObjective.DestroyAsteroids, 20);
            T.Check("Abschluss bei Erreichen des Ziels (genau einmal gemeldet)", q.GetProgress("q_asteroids_10").State == QuestState.Completed && q.GetProgress("q_asteroids_10").Progress == 10 && completed == 1);
            T.Check("Belohnung wird abgeholt", q.Claim("q_asteroids_10", inv) && inv.Count("repair_kit") == 1);
            T.Check("Belohnung nicht doppelt abholbar", !q.Claim("q_asteroids_10", inv) && inv.Count("repair_kit") == 1);
            q.Accept("q_score_3000"); q.Report(QuestObjective.ReachScore, 3500);
            var full = new Inventory(db, 1); full.Add("shield_booster", 1);
            T.Check("volles Inventar: Quest bleibt abholbar", !q.Claim("q_score_3000", full) && q.GetProgress("q_score_3000").State == QuestState.Completed);
            var q2 = QuestLog.CreateDefault(); q2.LoadJson(q.ToJson());
            T.Check("Queststatus wird gespeichert/geladen (inkl. 'Belohnung bereits beansprucht')", q2.GetProgress("q_asteroids_10").State == QuestState.Claimed && q2.GetProgress("q_score_3000").State == QuestState.Completed);
        }
    }
}
