using System;
using System.Collections.Generic;

namespace StarWars.Sim
{
    public static class PvpModes
    {
        public const string LastSurvivor = "last_survivor";
        public const string Points = "points";
        public static bool IsValid(string m) => m == LastSurvivor || m == Points;
    }

    public sealed class DuelStats
    {
        public int ShotsFired, Hits, Kills, DamageDealt, SurvivalTimeMs;
        public double Accuracy => ShotsFired <= 0 ? 0.0 : (double)Hits / ShotsFired * 100.0;
    }

    public sealed class DuelPlayer
    {
        public string Id, Name, ShipKey, Role;
        public PlayerShip Ship;
        public DuelStats Stats = new DuelStats();
        public int Score;
        public double RespawnAtMs, AliveSinceMs;
        public bool Eliminated;
        public bool Alive => !Eliminated && RespawnAtMs <= 0.0 && Ship.Lives > 0;
    }

    public sealed class DuelProjectile
    {
        public string Id, OwnerId, Weapon;
        public PlayerProjectile Obj;
        public int Damage;
    }

    public sealed class DuelEffect
    {
        public string Id; public double X, Y, Scale, CreatedAtMs;
    }

    public struct PvpPlayerInfo
    {
        public string Id, Name, Ship;
        public PvpPlayerInfo(string id, string name, string ship) { Id = id; Name = name; Ship = ship; }
    }

    /// <summary>
    /// Autoritative Zwei-Spieler-Welt (game/pvp_duel.py). Der Host (oder der lokale PC) besitzt den Zustand:
    /// Spieler, Projektile, Asteroiden, Kollisionen, Punkte und Systemwechsel. Clients erhalten nur Snapshots.
    /// </summary>
    public sealed class PvpWorld
    {
        public const int WorldWidth = GameConstants.Width, WorldHeight = GameConstants.Height;
        public readonly string Mode;
        public readonly SimClock Clock = new SimClock();
        public readonly ISimRandom Rng;
        public readonly List<DuelPlayer> Players = new List<DuelPlayer>();
        public readonly List<DuelProjectile> Projectiles = new List<DuelProjectile>();
        public readonly Dictionary<string, Asteroid> Asteroids = new Dictionary<string, Asteroid>();
        public readonly Dictionary<string, DuelEffect> Effects = new Dictionary<string, DuelEffect>();
        public readonly BackgroundDirector Background;
        public readonly HitLedger Ledger = new HitLedger();
        public bool MatchOver { get; private set; }
        public Dictionary<string, object> Result { get; private set; }
        public double ResultStartedMs { get; private set; }
        public int MatchElapsedMs { get; private set; }
        private int _asteroidTimer, _idCounter;
        private string _lastTransitionSignature;
        private double _matchStartMs;

        public PvpWorld(string mode, IList<PvpPlayerInfo> players, ISimRandom rng = null)
        {
            if (players == null || players.Count != GameConstants.PvpMaxPlayers) throw new ArgumentException("PvP benötigt genau zwei Spieler.");
            Mode = PvpModes.IsValid(mode) ? mode : GameConstants.PvpDefaultMode;
            Rng = rng ?? new SimRandom();
            Background = new BackgroundDirector(WorldWidth, WorldHeight, Clock, Rng, true);
            for (int i = 0; i < players.Count; i++)
            {
                var info = players[i];
                string ship = ShipCatalog.IsValid(info.Ship) ? info.Ship : "xwing";
                var p = new DuelPlayer { Id = info.Id, Name = Truncate(string.IsNullOrWhiteSpace(info.Name) ? "Spieler" : info.Name, GameConstants.MaxNameLength), ShipKey = ship, Role = i == 0 ? "bottom" : "top" };
                p.Ship = new PlayerShip(ShipCatalog.Get(ship), WorldWidth, WorldHeight, Clock) { Speed = GameConstants.PvpPlayerSpeed };
                ResetSpawn(p, 0);
                Players.Add(p);
            }
            _matchStartMs = Clock.NowMs;
        }

        private static string Truncate(string s, int n) => s.Length <= n ? s : s.Substring(0, n);
        private string NewId(string prefix) => prefix + (++_idCounter).ToString("x");
        public DuelPlayer Get(string id) { foreach (var p in Players) if (p.Id == id) return p; return null; }

        private void ResetSpawn(DuelPlayer p, int invulnerableMs)
        {
            p.Ship.X = WorldWidth / 2 - p.Ship.Width / 2;
            p.Ship.Y = p.Role == "bottom" ? WorldHeight - p.Ship.Height - GameConstants.PvpPlayerBottomMargin : GameConstants.PvpPlayerTopMargin;
            p.Ship.UpdateHitbox();
            p.Ship.InvulnerableUntilMs = Clock.NowMs + Math.Max(0, invulnerableMs);
            p.RespawnAtMs = 0.0;
            p.AliveSinceMs = Clock.NowMs;
        }

        // ------------------------------------------------------------------ Tick
        /// <param name="inputs">Eingaben je Spieler-ID (fehlende Einträge = keine Eingabe). Laser/Torpedo sind Ereignisse.</param>
        public void Step(IDictionary<string, PlayerInput> inputs)
        {
            Clock.Advance(GameConstants.TickMs);
            MatchElapsedMs = (int)(Clock.NowMs - _matchStartMs);
            HandleRespawns();

            foreach (var p in Players)
            {
                PlayerInput inp = default;
                if (inputs != null) inputs.TryGetValue(p.Id, out inp);
                MovePlayer(p, inp.Left, inp.Right);
            }
            foreach (var p in Players)
            {
                PlayerInput inp = default;
                if (inputs != null) inputs.TryGetValue(p.Id, out inp);
                if (inp.Laser) FireWeapon(p.Id, "laser");
                if (inp.Torpedo) FireWeapon(p.Id, "torpedo");
            }

            UpdateProjectiles();
            UpdateAsteroids();
            HandleCollisions();
            UpdateSystemTransition();

            if (!MatchOver)
            {
                var result = ComputeResult();
                if (result != null) { MatchOver = true; Result = result; ResultStartedMs = Clock.NowMs; }
            }
        }

        /// <summary>Gegner getrennt/ausgefallen: gilt als eliminiert, der Verbleibende gewinnt.</summary>
        public void MarkDisconnected(string playerId)
        {
            var p = Get(playerId);
            if (p == null || p.Eliminated) return;
            p.Eliminated = true; p.RespawnAtMs = 0.0; p.Ship.Lives = 0;
            if (!MatchOver)
            {
                var remaining = Players.FindAll(x => !x.Eliminated);
                MatchOver = true;
                Result = MakeResult(remaining.Count == 1 ? remaining[0].Id : null);
                ResultStartedMs = Clock.NowMs;
            }
        }

        private void MovePlayer(DuelPlayer p, bool left, bool right)
        {
            if (p.Eliminated || p.RespawnAtMs > 0.0 || p.Ship.Lives <= 0) return;
            if (left && !right) p.Ship.MoveLeft();
            else if (right && !left) p.Ship.MoveRight(WorldWidth);
        }

        private void HandleRespawns()
        {
            foreach (var p in Players)
            {
                if (p.Eliminated || p.RespawnAtMs <= 0.0) continue;
                if (Clock.NowMs < p.RespawnAtMs) continue;
                ResetSpawn(p, GameConstants.PvpRespawnInvulnerabilityMs);
            }
        }

        // ------------------------------------------------------------------ Waffen & Schaden
        public void FireWeapon(string playerId, string weapon)
        {
            var p = Get(playerId);
            if (p == null || p.Eliminated || p.Ship == null || p.Ship.Lives <= 0) return;
            if (p.RespawnAtMs > 0.0) return;   // Schiff ist während der Respawn-Verzögerung ausgeblendet
            int dir = p.Role == "bottom" ? -1 : 1;
            if (weapon == "laser")
            {
                var shots = p.Ship.Shoot();
                foreach (var s in shots)
                {
                    s.Direction = dir; s.OwnerId = p.Id; s.Id = NewId("p");
                    Projectiles.Add(new DuelProjectile { Id = s.Id, OwnerId = p.Id, Weapon = "laser", Obj = s, Damage = GameConstants.PvpLaserDamage });
                }
                p.Stats.ShotsFired += shots.Count;
            }
            else if (weapon == "torpedo")
            {
                var t = p.Ship.FireTorpedo();
                if (t == null) return;
                t.Direction = dir; t.OwnerId = p.Id; t.Id = NewId("p");
                Projectiles.Add(new DuelProjectile { Id = t.Id, OwnerId = p.Id, Weapon = "torpedo", Obj = t, Damage = GameConstants.PvpTorpedoDamage });
                p.Stats.ShotsFired += 1;
            }
        }

        private void AddScore(DuelPlayer p, int amount) { p.Score = Math.Max(0, p.Score + amount); }

        private void AddEffect(double x, double y, double scale)
        {
            string id = NewId("e");
            Effects[id] = new DuelEffect { Id = id, X = x, Y = y, Scale = scale, CreatedAtMs = Clock.NowMs };
        }

        private void ApplyPlayerDamage(string attackerId, DuelPlayer victim, int damage)
        {
            if (victim.Eliminated || victim.Ship.Lives <= 0 || victim.Ship.IsInvulnerable) return;
            var attacker = attackerId != null ? Get(attackerId) : null;
            bool died = victim.Ship.TakeDamage(damage);
            AddEffect(victim.Ship.Hitbox.CenterX, victim.Ship.Hitbox.CenterY, 0.9);
            if (attacker != null)
            {
                attacker.Stats.Hits++; attacker.Stats.DamageDealt += damage;
                AddScore(attacker, GameConstants.PvpHitScore);
            }
            double now = Clock.NowMs;
            victim.Stats.SurvivalTimeMs += (int)Math.Max(0.0, now - victim.AliveSinceMs);
            if (died)
            {
                victim.Eliminated = true; victim.RespawnAtMs = 0.0;
                if (attacker != null) { attacker.Stats.Kills++; AddScore(attacker, GameConstants.PvpKillScore); }
                victim.Ship.Lives = 0; victim.Ship.InvulnerableUntilMs = 0;
            }
            else
            {
                victim.RespawnAtMs = now + GameConstants.PvpRespawnDelayMs;
                victim.AliveSinceMs = 0.0;
                victim.Ship.InvulnerableUntilMs = now + GameConstants.PvpRespawnDelayMs;
            }
        }

        private void UpdateProjectiles()
        {
            for (int i = Projectiles.Count - 1; i >= 0; i--)
            {
                var pr = Projectiles[i];
                pr.Obj.Update();
                if (pr.Obj.Rect.Bottom < 0 || pr.Obj.Rect.Top > WorldHeight) Projectiles.RemoveAt(i);
            }
            if (Projectiles.Count > GameConstants.PvpMaxProjectiles)
                Projectiles.RemoveRange(0, Projectiles.Count - GameConstants.PvpMaxProjectiles);
        }

        // ------------------------------------------------------------------ Asteroiden
        private void UpdateAsteroids()
        {
            var profile = Difficulties.Get(GameConstants.DefaultDifficulty);
            double density = profile.AsteroidDensity * (1.0 + Background.SystemBonus * 0.80);
            int interval = Math.Max(GameConstants.PvpAsteroidMinSpawnInterval, (int)(GameConstants.PvpAsteroidBaseSpawnInterval / Math.Max(0.35, density)));
            _asteroidTimer++;
            if (_asteroidTimer >= interval) { SpawnSafeAsteroid(); _asteroidTimer = 0; }

            foreach (var kv in new List<KeyValuePair<string, Asteroid>>(Asteroids))
            {
                var a = kv.Value;
                a.Update();
                // Original: zwei Definitionen von _update_host_asteroids – die zweite (nur y > Höhe) verdeckte die erste und ließ
                // seitlich/oben davonfliegende Asteroiden nie verschwinden. Hier gilt die ursprünglich beabsichtigte Bereichsprüfung.
                if (a.X > WorldWidth + a.Width * 2 || a.X < -a.Width * 3 || a.Y > WorldHeight + a.Height * 2 || a.Y < -a.Height * 3)
                    Asteroids.Remove(kv.Key);
            }
        }

        private void SpawnSafeAsteroid()
        {
            if (Asteroids.Count >= GameConstants.PvpAsteroidMax) return;
            var profile = Difficulties.Get(GameConstants.DefaultDifficulty);
            double bonus = Background.SystemBonus;
            double speedMul = Background.AsteroidSpeedMultiplier * profile.AsteroidSpeed * (1.0 + bonus * 0.70);
            double sizeMul = profile.AsteroidSize * (1.0 + bonus * 0.18);
            string[] directions = { "left_to_right", "right_to_left", "diag_left_bottom_to_right_top", "diag_right_top_to_left_bottom", "diag_left_top_to_right_bottom", "diag_right_bottom_to_left_top" };
            string direction = Rng.Choice(directions);
            for (int attempt = 0; attempt < GameConstants.PvpAsteroidSpawnAttempts; attempt++)
            {
                var candidate = new Asteroid(WorldWidth, WorldHeight, Rng, sizeMul, speedMul);
                LanePosition(direction, candidate, out var x, out var y, out var vx, out var vy);
                candidate.X = x; candidate.Y = y; candidate.Vx = vx; candidate.Vy = vy;
                var rect = candidate.GetRect();
                bool safe = true;
                foreach (var p in Players)
                {
                    var expanded = p.Ship.Hitbox.Inflate(GameConstants.PvpAsteroidPlayerSafeDistance * 2, GameConstants.PvpAsteroidPlayerSafeDistance * 2);
                    if (rect.Colliderect(expanded)) { safe = false; break; }
                }
                if (safe) { candidate.Id = NewId("a"); Asteroids[candidate.Id] = candidate; return; }
            }
        }

        private void LanePosition(string direction, Asteroid a, out double x, out double y, out double vx, out double vy)
        {
            int w = WorldWidth, h = WorldHeight;
            switch (direction)
            {
                case "left_to_right":
                    x = -a.Width - Rng.Int(12, 80);
                    y = Rng.Int((int)(h * 0.12), Math.Max((int)(h * 0.12), (int)(h * 0.82) - a.Height));
                    vx = Rng.Uniform(1.3, 2.6) * (1.15 + Math.Max(0.0, (w / 800.0) - 1.0) * 0.6);
                    vy = Rng.Uniform(-0.5, 0.7); return;
                case "right_to_left":
                    x = w + Rng.Int(12, 80);
                    y = Rng.Int((int)(h * 0.18), Math.Max((int)(h * 0.18), (int)(h * 0.82) - a.Height));
                    vx = -Rng.Uniform(1.3, 2.6) * (1.15 + Math.Max(0.0, (w / 800.0) - 1.0) * 0.6);
                    vy = Rng.Uniform(-0.5, 0.7); return;
                case "diag_left_bottom_to_right_top":
                    x = Rng.Int(-(int)(w * 0.25), -a.Width); y = h + Rng.Int(20, (int)(h * 0.22));
                    vx = Rng.Uniform(1.0, 2.1); vy = -Rng.Uniform(1.0, 1.9); return;
                case "diag_right_top_to_left_bottom":
                    x = w + Rng.Int(20, (int)(w * 0.20)); y = -Rng.Int(20, (int)(h * 0.20));
                    vx = -Rng.Uniform(1.0, 2.1); vy = Rng.Uniform(1.0, 1.9); return;
                case "diag_left_top_to_right_bottom":
                    x = -Rng.Int(20, (int)(w * 0.20)); y = Rng.Int(-(int)(h * 0.20), 0);
                    vx = Rng.Uniform(1.0, 2.1); vy = Rng.Uniform(1.0, 1.9); return;
                default:
                    x = w + Rng.Int(20, (int)(w * 0.20)); y = h + Rng.Int(20, (int)(h * 0.22));
                    vx = -Rng.Uniform(1.0, 2.1); vy = -Rng.Uniform(1.0, 1.9); return;
            }
        }

        // ------------------------------------------------------------------ Kollisionen
        private void HandleCollisions()
        {
            foreach (var pr in Projectiles.ToArray())
            {
                if (!Projectiles.Contains(pr)) continue;
                bool hitAsteroid = false;
                foreach (var kv in new List<KeyValuePair<string, Asteroid>>(Asteroids))
                {
                    if (!kv.Value.GetRect().Colliderect(pr.Obj.Rect)) continue;
                    var owner = Get(pr.OwnerId);
                    if (owner != null) AddScore(owner, kv.Value.GetPoints());
                    AddEffect(kv.Value.X + kv.Value.Width / 2.0, kv.Value.Y + kv.Value.Height / 2.0, Math.Max(0.3, kv.Value.Scale));
                    Asteroids.Remove(kv.Key);
                    hitAsteroid = true; break;
                }
                if (hitAsteroid) { Projectiles.Remove(pr); continue; }

                foreach (var victim in Players)
                {
                    if (victim.Id == pr.OwnerId || victim.Eliminated || victim.RespawnAtMs > 0.0) continue;
                    if (victim.Ship.IsInvulnerable) continue;
                    if (!victim.Ship.Hitbox.Colliderect(pr.Obj.Rect)) continue;
                    // Ein Projektil darf genau einmal wirken (Ledger schützt gegen Doppelwertung).
                    if (Ledger.TryRegister(pr.Id)) ApplyPlayerDamage(pr.OwnerId, victim, pr.Damage);
                    Projectiles.Remove(pr);
                    break;
                }
            }

            foreach (var kv in new List<KeyValuePair<string, Asteroid>>(Asteroids))
            {
                var rect = kv.Value.GetRect();
                foreach (var p in Players)
                {
                    if (p.Eliminated || p.RespawnAtMs > 0.0 || p.Ship.IsInvulnerable) continue;
                    if (!rect.Colliderect(p.Ship.Hitbox)) continue;
                    ApplyPlayerDamage(null, p, 1);
                    Asteroids.Remove(kv.Key);
                    AddEffect(kv.Value.X + kv.Value.Width / 2.0, kv.Value.Y + kv.Value.Height / 2.0, Math.Max(0.3, kv.Value.Scale));
                    break;
                }
            }
        }

        private void UpdateSystemTransition()
        {
            int total = 0; foreach (var p in Players) total += p.Score;
            Background.Update(total);
            string signature = Background.Transition.Active ? Background.Transition.TargetOrderIndex + ":" + Background.Transition.To?.IdName : null;
            if (signature != _lastTransitionSignature)
            {
                if (signature != null) { Asteroids.Clear(); Projectiles.Clear(); _asteroidTimer = 0; }
                _lastTransitionSignature = signature;
            }
        }

        // ------------------------------------------------------------------ Ergebnis
        private Dictionary<string, object> ComputeResult()
        {
            var alive = Players.FindAll(p => !p.Eliminated);
            if (Mode == PvpModes.LastSurvivor)
            {
                int eliminated = Players.Count - alive.Count;
                if (eliminated >= 1 && alive.Count <= 1) return MakeResult(alive.Count == 1 ? alive[0].Id : null);
                return null;
            }
            if (MatchElapsedMs >= GameConstants.PvpScoreLimitMs)
            {
                var rows = new List<DuelPlayer>(Players);
                rows.Sort((a, b) => b.Score.CompareTo(a.Score));
                if (rows.Count >= 2 && rows[0].Score == rows[1].Score) return MakeResult(null);
                return MakeResult(rows.Count > 0 ? rows[0].Id : null);
            }
            return null;
        }

        private Dictionary<string, object> MakeResult(string winnerId)
        {
            var players = new List<object>();
            foreach (var p in Players) players.Add(PlayerSnapshot(p));
            return new Dictionary<string, object> { { "winner_id", winnerId }, { "mode", Mode }, { "players", players } };
        }

        public Dictionary<string, object> PlayerSnapshot(DuelPlayer p)
        {
            int survival = p.Stats.SurvivalTimeMs;
            if (!p.Eliminated && p.AliveSinceMs > 0.0) survival += (int)Math.Max(0.0, Clock.NowMs - p.AliveSinceMs);
            return new Dictionary<string, object>
            {
                { "id", p.Id }, { "name", p.Name }, { "ship", p.ShipKey }, { "role", p.Role },
                { "x", (double)p.Ship.X }, { "y", (double)p.Ship.Y }, { "width", (long)p.Ship.Width }, { "height", (long)p.Ship.Height },
                { "score", (long)p.Score }, { "lives", (long)p.Ship.Lives }, { "alive", p.Alive }, { "eliminated", p.Eliminated },
                { "kills", (long)p.Stats.Kills }, { "hits", (long)p.Stats.Hits }, { "shots", (long)p.Stats.ShotsFired },
                { "damage", (long)p.Stats.DamageDealt }, { "survival_ms", (long)Math.Max(0, survival) }, { "invulnerable", p.Ship.IsInvulnerable },
            };
        }

        /// <summary>Autoritativer Snapshot (Format wie im Original, version 1).</summary>
        public Dictionary<string, object> BuildSnapshot()
        {
            var asteroids = new List<object>();
            foreach (var kv in Asteroids)
                asteroids.Add(new Dictionary<string, object> { { "id", kv.Key }, { "x", kv.Value.X }, { "y", kv.Value.Y }, { "width", (long)kv.Value.Width }, { "height", (long)kv.Value.Height }, { "scale", kv.Value.Scale }, { "frame", (long)kv.Value.Frame } });
            var projectiles = new List<object>();
            foreach (var pr in Projectiles)
                projectiles.Add(new Dictionary<string, object> { { "id", pr.Id }, { "owner_id", pr.OwnerId }, { "weapon", pr.Weapon }, { "x", (double)pr.Obj.Rect.X }, { "y", (double)pr.Obj.Rect.Y }, { "width", (long)pr.Obj.Rect.W }, { "height", (long)pr.Obj.Rect.H } });
            var effects = new List<object>();
            foreach (var kv in new List<KeyValuePair<string, DuelEffect>>(Effects))
            {
                int age = (int)(Clock.NowMs - kv.Value.CreatedAtMs);
                if (age > GameConstants.PvpExplosionDurationMs) { Effects.Remove(kv.Key); continue; }
                effects.Add(new Dictionary<string, object> { { "id", kv.Key }, { "x", kv.Value.X }, { "y", kv.Value.Y }, { "scale", kv.Value.Scale }, { "age_ms", (long)age } });
            }
            var order = new List<object>(); foreach (var s in Background.Systems.Order) order.Add(s.IdName);
            var players = new List<object>(); foreach (var p in Players) players.Add(PlayerSnapshot(p));
            var transition = new Dictionary<string, object> { { "active", Background.Transition.Active } };
            if (Background.Transition.Active)
            {
                transition["target_index"] = (long)Background.Transition.TargetOrderIndex;
                transition["from_index"] = (long)Background.SystemIndex;
                transition["elapsed_ms"] = (long)Math.Max(0, (int)(Clock.NowMs - Background.Transition.StartMs));
                transition["duration_ms"] = (long)Background.Transition.DurationMs;
            }
            int total = 0; foreach (var p in Players) total += p.Score;
            return new Dictionary<string, object>
            {
                { "type", "pvp_snapshot" }, { "version", 1L }, { "mode", Mode }, { "source_width", (long)WorldWidth }, { "source_height", (long)WorldHeight },
                { "match_elapsed_ms", (long)MatchElapsedMs }, { "match_time_limit_ms", (long)GameConstants.PvpScoreLimitMs },
                { "system_index", (long)Background.SystemIndex }, { "system_name", Background.CurrentSystemName }, { "system_order", order },
                { "transition", transition }, { "players", players }, { "asteroids", asteroids }, { "projectiles", projectiles }, { "effects", effects },
                { "match_over", MatchOver }, { "result", Result }, { "global_score", (long)total },
            };
        }
    }
}
