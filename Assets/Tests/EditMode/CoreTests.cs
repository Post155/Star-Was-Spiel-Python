using System;
using System.Collections.Generic;
using System.IO;
using StarWars.Sim;

namespace StarWars.SimTests
{
    /// <summary>Vergleich mit Referenzwerten, die aus dem ORIGINAL-Python-Code erzeugt wurden (tools/gen_golden.py).</summary>
    public static class GoldenTests
    {
        public static void Run(string goldenPath)
        {
            var g = (Dictionary<string, object>)Json.Parse(File.ReadAllText(goldenPath));

            T.Group("Golden: EnemyManager (Schwierigkeit/Skalierung/Spawn/Balancing) vs. Python");
            int n = 0, bad = 0;
            foreach (Dictionary<string, object> r in (List<object>)g["manager"])
            {
                string diff = Json.Str(r, "diff"); int sys = (int)Json.Int(r, "system"); int score = (int)Json.Int(r, "score");
                var em = new EnemyManager(800, 600, new PlayerShip(ShipCatalog.XWing, 800, 600, new SimClock()), diff, new SimRandom(1));
                bool ok = Math.Abs(em.DifficultyScale(score, sys) - Json.Num(r, "scale")) < 1e-9
                    && em.MaxEnemies(score, sys) == Json.Int(r, "max")
                    && Math.Abs(em.SpawnIntervalBase(score, sys) - Json.Num(r, "interval")) < 1e-9
                    && EnemyManager.UnlockedTier(score) == Json.Int(r, "tier");
                var bal = Json.Obj(r, "bal");
                foreach (var kv in EnemyArchetypes.All)
                {
                    var b = em.BalancedArchetype(kv.Value, score, sys); var p = Json.Obj(bal, kv.Key);
                    ok &= b.MaxHp == Json.Int(p, "hp") && Math.Abs(b.MaxSpeed - Json.Num(p, "speed")) < 1e-9 && Math.Abs(b.Acceleration - Json.Num(p, "acc")) < 1e-9
                        && Math.Abs(b.Accuracy - Json.Num(p, "accuracy")) < 1e-9 && Math.Abs(b.ReactionMin - Json.Num(p, "rmin")) < 1e-9
                        && Math.Abs(b.ReactionMax - Json.Num(p, "rmax")) < 1e-9 && Math.Abs(b.DodgeChance - Json.Num(p, "dodge")) < 1e-9
                        && Math.Abs(b.TorpedoChance - Json.Num(p, "torp")) < 1e-9;
                }
                n++; if (!ok) { bad++; if (bad < 4) Console.WriteLine($"    Abweichung: {diff} sys={sys} score={score}"); }
            }
            T.Check($"{n} Kombinationen (4 Schwierigkeiten x 6 Systeme x 13 Punktestände x 4 Archetypen) stimmen exakt", bad == 0, bad + " Abweichungen");

            T.Group("Golden: EnemyMovement (Steuerung) vs. Python");
            foreach (Dictionary<string, object> r in (List<object>)g["movement"])
            {
                string key = Json.Str(r, "arch");
                var arch = EnemyArchetypes.All[key];
                var e = new EnemyShip("XWing", "tiefighter", arch, 800, 600, 12.0, -12.0, "attacker", new SimRandom(1));
                // Das Python-Referenzobjekt nutzt 96x96-Größe und feste Hitbox; EnemyShip hat die echten Maße -> Größe angleichen nicht möglich,
                // daher wird die Bewegung gegen ein identisch parametrisiertes Ersatzschiff geprüft (siehe unten).
                T.Check($"EnemyMovement[{key}] Referenzdaten vorhanden", ((List<object>)r["traj"]).Count == 16);
            }
            MovementParity(g);

            T.Group("Golden: Spielerschiffe (Position, Alpha-Hitbox, Laser, Torpedo) vs. Python");
            foreach (Dictionary<string, object> r in (List<object>)g["ships"])
            {
                string ship = Json.Str(r, "ship"); int left = (int)Json.Int(r, "moves_left");
                var p = new PlayerShip(ShipCatalog.Get(ship), 800, 600, new SimClock());
                if (left > 0) for (int i = 0; i < left; i++) p.MoveLeft();
                if (left < 0) for (int i = 0; i < 200; i++) p.MoveRight(800);
                var hb = (List<object>)r["hitbox"];
                bool ok = p.X == Json.Int(r, "x") && p.Y == Json.Int(r, "y") && p.Hitbox.X == (long)hb[0] && p.Hitbox.Y == (long)hb[1] && p.Hitbox.W == (long)hb[2] && p.Hitbox.H == (long)hb[3];
                if (left >= 0)
                {
                    var lasers = (List<object>)r["lasers"]; var shots = p.Shoot();
                    ok &= shots.Count == lasers.Count;
                    for (int i = 0; ok && i < lasers.Count; i++)
                    {
                        var l = (List<object>)lasers[i];
                        ok &= shots[i].Rect.X == (long)l[0] && shots[i].Rect.Y == (long)l[1] && shots[i].Rect.W == (long)l[2] && shots[i].Rect.H == (long)l[3];
                    }
                    var tor = r["torpedo"] as List<object>; var t = p.FireTorpedo();
                    ok &= (tor == null) == (t == null);
                    if (tor != null && t != null) ok &= t.Rect.X == (long)tor[0] && t.Rect.Y == (long)tor[1] && t.Rect.W == (long)tor[2] && t.Rect.H == (long)tor[3];
                }
                T.Check($"{ship} (links x{left}) stimmt mit Python überein", ok);
            }

            T.Group("Golden: Asteroiden (Größe, Punkte) vs. Python");
            int abad = 0, an = 0;
            foreach (Dictionary<string, object> r in (List<object>)g["asteroid_points"])
            {
                double scale = Json.Num(r, "scale");
                int pts = scale <= 0.5 ? 100 : (scale <= 0.75 ? 75 : 50);
                int w = PyMath.ScaleDim(256, scale);
                an++; if (pts != Json.Int(r, "points") || w != Json.Int(r, "w") || w != Json.Int(r, "h")) abad++;
            }
            T.Check($"{an} Asteroiden: Punktwert und Pixelgröße identisch", abad == 0, abad + " Abweichungen");
            var rng = new SimRandom(5); bool scaleOk = true; var scales = new HashSet<double>();
            for (int i = 0; i < 400; i++) { var a = new Asteroid(800, 600, rng, 1.0, 1.0); scales.Add(a.Scale); scaleOk &= a.Width == PyMath.ScaleDim(256, a.Scale) && a.GetPoints() == (a.Scale <= 0.5 ? 100 : a.Scale <= 0.75 ? 75 : 50); }
            T.Check("Asteroid-Skalen stammen aus {0.25,0.5,0.75,1.0}", scales.SetEquals(new[] { 0.25, 0.5, 0.75, 1.0 }) && scaleOk);
        }

        /// <summary>Bewegung gegen Python: gleiche Startparameter wie das Referenzobjekt (96x96, x=12, y=-12).</summary>
        private static void MovementParity(Dictionary<string, object> g)
        {
            foreach (Dictionary<string, object> r in (List<object>)g["movement"])
            {
                string key = Json.Str(r, "arch");
                var e = TestShip.Make(EnemyArchetypes.All[key]);
                var mv = new EnemyMovement(e);
                var targets = new List<double[]>();
                for (int i = 0; i < 60; i++) targets.Add(new[] { 500.0, 200.0 });
                for (int i = 0; i < 60; i++) targets.Add(new[] { 100.0, 300.0 });
                for (int i = 0; i < 40; i++) targets.Add(new[] { 700.0, 100.0 });
                bool ok = true; int idx = 0;
                var traj = (List<object>)r["traj"];
                for (int i = 0; i < targets.Count; i++)
                {
                    mv.Update(1.0 / 60, targets[i][0], targets[i][1], i == 70 ? 120.0 : 0.0);
                    if (i % 10 == 9)
                    {
                        var rec = (List<object>)traj[idx++];
                        ok &= Math.Abs(e.X - Convert.ToDouble(rec[1])) < 1e-9 && Math.Abs(e.Y - Convert.ToDouble(rec[2])) < 1e-9
                            && Math.Abs(e.Vx - Convert.ToDouble(rec[3])) < 1e-9 && Math.Abs(e.Vy - Convert.ToDouble(rec[4])) < 1e-9;
                    }
                }
                T.Check($"EnemyMovement[{key}]: 160 Ticks Trajektorie identisch zu Python (Toleranz 1e-9)", ok);
            }
        }
    }

    /// <summary>EnemyShip mit den Maßen des Python-Referenzobjekts (96x96, Hitbox 80x80).</summary>
    public static class TestShip
    {
        public static EnemyShip Make(EnemyArchetype a)
        {
            // XWing/standard hat 96x96; Archetypen skalieren die Größe -> für den Vergleich wird immer eine 96x96-Variante genutzt.
            var e = new EnemyShip("XWing", "tiefighter", Fixed96(a), 800, 600, 12.0, -12.0, "attacker", new SimRandom(1));
            return e;
        }
        private static EnemyArchetype Fixed96(EnemyArchetype a) { var c = a.Clone(); c.VisualScaleMultiplier = 1.0; c.Key = "standard"; return c; }
    }
}
