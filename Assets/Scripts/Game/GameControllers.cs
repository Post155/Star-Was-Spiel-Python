using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>Gemeinsame Basis: fester 60-Hz-Takt (Akkumulator), schwarze Letterbox-Kamera, Overlay-Hilfen.</summary>
    public abstract class GameControllerBase : MonoBehaviour
    {
        private double _acc;
        private GameObject _blackCam;
        protected Canvas Overlay;

        protected void EnsureBlackCamera()
        {
            if (_blackCam != null) return;
            _blackCam = new GameObject("BlackCamera");
            var cam = _blackCam.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = Color.black; cam.cullingMask = 0; cam.depth = -100;
        }

        /// <summary>Führt so viele 1/60-s-Ticks aus, wie die vergangene Zeit erfordert (max. 5 pro Frame, um Spiralen zu vermeiden).</summary>
        protected void RunTicks(Action tick)
        {
            _acc += Math.Min(Time.unscaledDeltaTime, 0.25f);
            int n = 0;
            while (_acc >= GameConstants.TickSeconds && n < 5) { tick(); _acc -= GameConstants.TickSeconds; n++; }
            if (n >= 5) _acc = 0;
        }

        protected Text OverlayText(string text, Vector2 aMin, Vector2 aMax, int size, Color color, TextAnchor anchor = TextAnchor.MiddleCenter, FontStyle style = FontStyle.Bold)
        {
            if (Overlay == null) Overlay = Ui.CreateCanvas("Overlay", 1280, 720, null, 50);
            return Ui.LabelAt(Overlay.transform, text, aMin, aMax, size, anchor, color, style);
        }

        protected static void GoToMenu() { AppState.LeaveNetwork(); SceneManager.LoadScene(SceneNames.MainMenu); }

        protected static string FormatMs(int ms) { int s = Math.Max(0, ms / 1000); return $"{s / 60}:{s % 60:00}"; }
    }

    // ====================================================================== Einzelspieler
    public sealed class SinglePlayerController : GameControllerBase
    {
        private SinglePlayerWorld _world; private WorldView _view; private InputAccumulator _input;
        private GameObject _deathPanel; private bool _deathHandled; private bool _record;

        private void Start()
        {
            EnsureBlackCamera();
            var setup = AppState.Players[0];
            _input = new InputAccumulator(ControlScheme.Solo);
            _world = new SinglePlayerWorld(GameConstants.Width, GameConstants.Height, setup.Ship, setup.Difficulty);
            var stage = new Stage("Single", Vector3.zero, GameConstants.Width, GameConstants.Height, Letterbox.Fit(), 0) { ViewportFn = () => Letterbox.Fit() };
            _view = new WorldView(stage, ShipCatalog.Get(setup.Ship).Faction == Faction.Rebels);
            Progression.Attach(_world);
            _world.PlayerDamaged += lives => SoundBank.Play(Sfx.Hit);
            _world.AsteroidDestroyed += (a, p) => SoundBank.Play(Sfx.Explosion, 0.6f);
            _world.EnemyDestroyed += (e, p) => SoundBank.Play(Sfx.Explosion);
        }

        private void Update()
        {
            _input.Sample();
            if (InputAccumulator.KeyDown(KeyCode.H)) _view.ShowHitbox = !_view.ShowHitbox;
            if (InputAccumulator.KeyDown(KeyCode.Alpha1)) SwitchShip("xwing");
            if (InputAccumulator.KeyDown(KeyCode.Alpha2)) SwitchShip("milleniumfalcon");
            if (InputAccumulator.KeyDown(KeyCode.Alpha3)) SwitchShip("tiefighter");
            if (InputAccumulator.KeyDown(KeyCode.Alpha4)) SwitchShip("battledroid");
            if (InputAccumulator.KeyDown(KeyCode.Escape) && !_deathHandled) { Progression.Save(_world.Score); GoToMenu(); return; }

            string lastWarning = _world.WarningText;
            RunTicks(() =>
            {
                var inp = _input.Take();
                if (!_world.Dead)
                {
                    if (inp.Laser) SoundBank.Play(Sfx.Laser, 0.5f);
                    if (inp.Torpedo && _world.Player.Info.HasTorpedo) SoundBank.Play(Sfx.Torpedo, 0.7f);
                }
                _world.Step(inp);
            });
            if (_world.WarningText != null && _world.WarningText != lastWarning) SoundBank.Play(Sfx.Warning);
            _view.Draw(_world);
            if (_world.Dead && !_deathHandled) ShowDeath();
            if (_deathHandled && InputAccumulator.KeyDown(KeyCode.R)) Restart();
            if (_deathHandled && InputAccumulator.KeyDown(KeyCode.Escape)) GoToMenu();
        }

        private void SwitchShip(string key) { _world.SwitchShip(key); _view.SetFaction(ShipCatalog.Get(key).Faction == Faction.Rebels); }

        private void ShowDeath()
        {
            _deathHandled = true;
            _record = AppState.Save.SubmitScore(_world.Score);
            Progression.Save(_world.Score);
            var canvas = Ui.CreateCanvas("DeathCanvas", 1280, 720, null, 50);
            _deathPanel = canvas.gameObject;
            Ui.Background(canvas.transform, new Color(0, 0, 0, 0.7f));
            var col = Ui.Column(canvas.transform, 600, 14);
            Ui.Line(col, "GAME OVER", 80, Ui.Danger, 110, FontStyle.Bold);
            Ui.Line(col, "DEINE PUNKTZAHL: " + _world.Score, 36, Color.white, 50, FontStyle.Bold);
            Ui.Line(col, _record ? "NEUER REKORD!" : "PERSÖNLICHER REKORD: " + AppState.Save.Data.Highscore, 30, _record ? Ui.Gold : Ui.Grey, 44, FontStyle.Bold);
            Ui.Spacer(col, 16);
            Ui.Btn(col, "NEUSTART  [R]", Restart, 60, 28);
            Ui.Btn(col, "BEENDEN  [Esc]", GoToMenu, 60, 28);
        }

        private void Restart() { SceneManager.LoadScene(SceneNames.Singleplayer); }
    }

    /// <summary>Verbindet Spielereignisse mit Quests/Inventar und schreibt den Fortschritt (neues System, siehe PARITY_STATUS).</summary>
    public static class Progression
    {
        public static void Attach(SinglePlayerWorld world)
        {
            AppState.EnsureServices();
            world.AsteroidDestroyed += (a, p) => AppState.Quests.Report(QuestObjective.DestroyAsteroids, 1);
            world.EnemyDestroyed += (e, p) => AppState.Quests.Report(QuestObjective.DestroyEnemies, 1);
            world.ScoreChanged += s => AppState.Quests.Report(QuestObjective.ReachScore, s);
            world.SystemChanged += st => AppState.Quests.Report(QuestObjective.EnterSystems, 1);
        }

        public static void Save(int score) { AppState.PersistProgress(); }
    }

    // ====================================================================== Lokaler Punktekampf
    public sealed class PointsFightController : GameControllerBase
    {
        private PointsFightMatch _match; private WorldView[] _views = new WorldView[2]; private readonly InputAccumulator[] _inputs = new InputAccumulator[2];
        private Text _timer, _rank; private GameObject _rankPanel; private bool _resultShown;

        private void Start()
        {
            EnsureBlackCamera();
            var cfgs = new PointsPlayerConfig[2];
            for (int i = 0; i < 2; i++)
            {
                var p = AppState.Players[i];
                cfgs[i] = new PointsPlayerConfig { Name = p.Name, Ship = p.Ship, Faction = p.Faction, Difficulty = p.Difficulty };
            }
            _match = new PointsFightMatch(cfgs[0], cfgs[1]);
            _inputs[0] = new InputAccumulator(ControlScheme.Player1Wasd); _inputs[1] = new InputAccumulator(ControlScheme.Player2Arrows);
            var box = Letterbox.Fit();
            for (int i = 0; i < 2; i++)
            {
                int side = i;
                var stage = new Stage("World" + (i + 1), new Vector3(10000f * (i + 1), 0, 0), PointsFightMatch.WorldWidth, PointsFightMatch.WorldHeight, Letterbox.Sub(box, 0.5f * i, 0.5f), i)
                { ViewportFn = () => Letterbox.Sub(Letterbox.Fit(), 0.5f * side, 0.5f) };
                _views[i] = new WorldView(stage, ShipCatalog.Get(cfgs[i].Ship).Faction == Faction.Rebels);
                _views[i].SetExtraText(cfgs[i].Name);
            }
            Overlay = Ui.CreateCanvas("Overlay", 1280, 720, null, 40);
            _timer = Ui.LabelAt(Overlay.transform, "", new Vector2(0.4f, 0.93f), new Vector2(0.6f, 1f), 34, TextAnchor.MiddleCenter, Ui.Gold, FontStyle.Bold);
            var divider = Ui.Rect(Overlay.transform, "Divider", new Vector2(0.5f, 0), new Vector2(0.5f, 1), new Vector2(-2, 0), new Vector2(2, 0)).gameObject.AddComponent<Image>(); divider.color = new Color(1, 1, 1, 0.5f);
            _rankPanel = Ui.Rect(Overlay.transform, "Rank", new Vector2(0.3f, 0.35f), new Vector2(0.7f, 0.65f), Vector2.zero, Vector2.zero).gameObject;
            Ui.Background(_rankPanel.transform, new Color(0, 0, 0, 0.75f));
            _rank = Ui.Label(_rankPanel.transform, "", 28, TextAnchor.MiddleCenter);
            _rankPanel.SetActive(false);
            for (int i = 0; i < 2; i++) { int idx = i; _match.Worlds[i].PlayerDamaged += l => SoundBank.Play(Sfx.Hit, 0.5f); _match.Worlds[i].AsteroidDestroyed += (a, p) => SoundBank.Play(Sfx.Explosion, 0.4f); }
        }

        private void Update()
        {
            for (int i = 0; i < 2; i++) _inputs[i].Sample();
            if (InputAccumulator.KeyDown(KeyCode.Escape)) { GoToMenu(); return; }
            RunTicks(() => _match.Step(_inputs[0].Take(), _inputs[1].Take()));

            for (int i = 0; i < 2; i++)
            {
                var me = _match.Worlds[i]; var other = _match.Worlds[1 - i];
                _views[i].Draw(me);
                _views[i].BeginGhosts();
                if (!other.Dead)
                {
                    var op = other.Player; var m = AssetMetrics.Ships[op.Info.Key];
                    _views[i].DrawGhost(op.Info.Key, (op.X + m.Width / 2.0) / other.Width, (double)op.Y / other.Height,
                        $"{_match.Configs[1 - i].Name} • {other.Score} • {other.Background.CurrentSystemName}");
                }
                _views[i].EndGhosts();
            }
            _timer.text = FormatMs(_match.RemainingMs);

            bool tab = InputAccumulator.KeyHeld(KeyCode.Tab);
            _rankPanel.SetActive(tab && !_match.Over);
            if (tab) _rank.text = RankText(true);

            if (_match.Over && !_resultShown) ShowResult();
        }

        private string RankText(bool live)
        {
            var rows = new List<(string, int, bool)>();
            for (int i = 0; i < 2; i++) rows.Add((_match.Configs[i].Name, _match.Worlds[i].Score, _match.Worlds[i].Dead));
            rows.Sort((a, b) => b.Item2.CompareTo(a.Item2));
            var sb = new StringBuilder(live ? "RANGLISTE (LIVE)\n\n" : "");
            int n = 1; foreach (var r in rows) sb.Append(n++).Append(". ").Append(r.Item1).Append("  –  ").Append(r.Item2).Append(r.Item3 ? "  (GAME OVER)" : "").Append('\n');
            return sb.ToString();
        }

        private void ShowResult()
        {
            _resultShown = true;
            var canvas = Ui.CreateCanvas("Result", 1280, 720, null, 60);
            Ui.Background(canvas.transform, new Color(0, 0, 0, 0.78f));
            var col = Ui.Column(canvas.transform, 700, 12);
            Ui.Line(col, "PUNKTEKAMPF BEENDET", 56, Ui.Gold, 80, FontStyle.Bold);
            string winner = _match.WinnerName();
            Ui.Line(col, winner != null ? "SIEGER: " + winner : "UNENTSCHIEDEN", 44, Color.white, 60, FontStyle.Bold);
            Ui.Line(col, RankText(false), 30, Color.white, 110);
            Ui.Btn(col, "Revanche", () => SceneManager.LoadScene(SceneNames.LocalPointsFight), 58, 26);
            Ui.Btn(col, "Hauptmenü", GoToMenu, 58, 26);
        }
    }

    // ====================================================================== PvP-Duell (lokal / LAN-Host / LAN-Client)
    public sealed class PvpController : GameControllerBase
    {
        private enum Kind { Local, Host, Client }
        private Kind _kind;
        private PvpWorld _world; private PvpHostDriver _host; private PvpClientDriver _client;
        private PvpView _view; private InputAccumulator _in1, _in2;
        private bool _resultShown; private double _overSince = -1;
        private string _localId, _localRole = "bottom";

        private void Start()
        {
            EnsureBlackCamera();
            _view = new PvpView(new Stage("Pvp", Vector3.zero, GameConstants.Width, GameConstants.Height, Letterbox.Fit(), 0) { ViewportFn = () => Letterbox.Fit() });
            if (AppState.Mode == GameMode.LocalLastSurvivor)
            {
                _kind = Kind.Local;
                var players = new List<PvpPlayerInfo>
                {
                    new PvpPlayerInfo("local_p1", AppState.Players[0].Name, AppState.Players[0].Ship),
                    new PvpPlayerInfo("local_p2", AppState.Players[1].Name, AppState.Players[1].Ship),
                };
                _world = new PvpWorld(PvpModes.LastSurvivor, players);
                _in1 = new InputAccumulator(ControlScheme.Player1Wasd); _in2 = new InputAccumulator(ControlScheme.Player2Arrows);
            }
            else
            {
                var net = AppState.Net;
                _localId = net.LocalId; _in1 = new InputAccumulator(ControlScheme.Solo);
                if (net.IsHost) { _kind = Kind.Host; _host = new PvpHostDriver(net, AppState.LanRule); _world = _host.World; }
                else { _kind = Kind.Client; _client = new PvpClientDriver(net); _localRole = "top"; }
            }
        }

        private void Update()
        {
            _in1.Sample(); _in2?.Sample();
            if (InputAccumulator.KeyDown(KeyCode.Escape) && !_resultShown) { GoToMenu(); return; }

            PvpFrame frame;
            switch (_kind)
            {
                case Kind.Local:
                    RunTicks(() => _world.Step(new Dictionary<string, PlayerInput> { { "local_p1", _in1.Take() }, { "local_p2", _in2.Take() } }));
                    frame = PvpFrame.From(_world); break;
                case Kind.Host:
                    RunTicks(() => _host.Step(_in1.Take()));
                    if (_host.Quit) { ShowResult(null, true); }
                    frame = PvpFrame.From(_world); break;
                default:
                    RunTicks(() => _client.Step(_in1.Take()));
                    var me = _client.View.Players.TryGetValue(_localId ?? "", out var p) ? p : null;
                    if (me != null) _localRole = me.Role;
                    frame = PvpFrame.From(_client.View);
                    if (_client.View.HostStopped) { ShowResult(null, true); }
                    break;
            }
            _view.Draw(frame, _localRole);

            if (frame.Over && !_resultShown)
            {
                if (_overSince < 0) _overSince = Time.unscaledTime;
                if ((Time.unscaledTime - _overSince) * 1000.0 >= GameConstants.PvpResultDelayMs) ShowResult(frame, false);
            }
            if (_resultShown && (InputAccumulator.KeyDown(KeyCode.Return) || InputAccumulator.KeyDown(KeyCode.Escape) || InputAccumulator.KeyDown(KeyCode.Space))) GoToMenu();
        }

        private void ShowResult(PvpFrame frame, bool hostStopped)
        {
            if (_resultShown) return;
            _resultShown = true;
            var canvas = Ui.CreateCanvas("Result", 1280, 720, null, 60);
            Ui.Background(canvas.transform, new Color(0, 0, 0, 0.82f));
            var col = Ui.Column(canvas.transform, 900, 10);
            if (hostStopped || frame == null)
            {
                Ui.Line(col, "HOST HAT DAS SPIEL BEENDET", 48, Ui.Danger, 90, FontStyle.Bold);
            }
            else
            {
                string winnerId = frame.Result != null && frame.Result.TryGetValue("winner_id", out var w) ? w as string : null;
                var winner = winnerId != null ? frame.Players.Find(p => p.Id == winnerId) : null;
                Ui.Line(col, winner != null ? "SIEGER: " + winner.Name : "UNENTSCHIEDEN", 60, winner != null ? Ui.Gold : Color.white, 90, FontStyle.Bold);
                var list = frame.Result != null ? Json.Arr(frame.Result, "players") : null;
                if (list != null)
                    foreach (var o in list)
                    {
                        var d = o as Dictionary<string, object>; if (d == null) continue;
                        long shots = Json.Int(d, "shots"), hits = Json.Int(d, "hits");
                        string acc = shots > 0 ? (hits * 100.0 / shots).ToString("0") + " %" : "–";
                        Ui.Line(col, $"{Json.Str(d, "name")}:  Punkte {Json.Int(d, "score")}   Abschüsse {Json.Int(d, "kills")}   Trefferquote {acc}   Überlebt {FormatMs((int)Json.Int(d, "survival_ms"))}   Schaden {Json.Int(d, "damage")}", 24, Color.white, 44);
                    }
            }
            Ui.Spacer(col, 14);
            Ui.Btn(col, "Weiter  [Enter]", GoToMenu, 60, 28);
        }
    }

    // ====================================================================== LAN-Punktekampf
    public sealed class LanPointsController : GameControllerBase
    {
        private SinglePlayerWorld _world; private WorldView _view; private InputAccumulator _input; private MultiplayerSession _net;
        private GameObject _board; private Text _boardText; private bool _deathShown; private Text _banner;

        private void Start()
        {
            EnsureBlackCamera();
            _net = AppState.Net; var setup = AppState.Players[0];
            _input = new InputAccumulator(ControlScheme.Solo);
            _world = new SinglePlayerWorld(GameConstants.Width, GameConstants.Height, setup.Ship, setup.Difficulty);
            var stage = new Stage("LanPoints", Vector3.zero, GameConstants.Width, GameConstants.Height, Letterbox.Fit(), 0) { ViewportFn = () => Letterbox.Fit() };
            _view = new WorldView(stage, ShipCatalog.Get(setup.Ship).Faction == Faction.Rebels);
            Progression.Attach(_world);
            _world.PlayerDamaged += l => SoundBank.Play(Sfx.Hit);
            _world.AsteroidDestroyed += (a, p) => SoundBank.Play(Sfx.Explosion, 0.5f);
            Overlay = Ui.CreateCanvas("Overlay", 1280, 720, null, 40);
            _board = Ui.Rect(Overlay.transform, "Board", new Vector2(0.28f, 0.2f), new Vector2(0.72f, 0.8f), Vector2.zero, Vector2.zero).gameObject;
            Ui.Background(_board.transform, new Color(0, 0, 0, 0.78f));
            _boardText = Ui.Label(_board.transform, "", 28, TextAnchor.MiddleCenter);
            _board.SetActive(false);
            _banner = Ui.LabelAt(Overlay.transform, "", new Vector2(0.2f, 0.9f), new Vector2(0.8f, 0.98f), 24, TextAnchor.MiddleCenter, Ui.Danger, FontStyle.Bold);
        }

        private void Update()
        {
            _input.Sample();
            _net.Poll();
            if (InputAccumulator.KeyDown(KeyCode.Escape)) { GoToMenu(); return; }
            if (_net.Client.HostDisconnected) _banner.text = "Der Host hat das Spiel beendet.";
            RunTicks(() => { var i = _input.Take(); if (i.Laser && !_world.Dead) SoundBank.Play(Sfx.Laser, 0.5f); _world.Step(i); });
            _net.UpdateLocalPoints(_world.Player, _world.Score, _world.Background.CurrentSystemName, !_world.Dead, _world.Dead && !_deathShown);
            _view.Draw(_world);
            _view.BeginGhosts();
            foreach (var r in _net.Remote.Values) if (r.Alive) { r.Interpolate(0.25); _view.DrawGhost(r.Ship, r.X, r.Y, $"{r.Name} • {r.Score} • {r.System}"); }
            _view.EndGhosts();

            bool tab = InputAccumulator.KeyHeld(KeyCode.Tab) || _world.Dead;
            _board.SetActive(tab);
            if (tab) _boardText.text = BoardText();
            if (_world.Dead && !_deathShown)
            {
                _deathShown = true; AppState.Save.SubmitScore(_world.Score); Progression.Save(_world.Score);
                var canvas = Ui.CreateCanvas("Death", 1280, 720, null, 60);
                var col = Ui.Column(canvas.transform, 500, 12, TextAnchor.LowerCenter, -250);
                Ui.Line(col, "GAME OVER – " + _world.Score + " Punkte", 40, Ui.Danger, 56, FontStyle.Bold);
                Ui.Btn(col, "Zurück zum Hauptmenü  [Esc]", GoToMenu, 56, 24);
            }
        }

        private string BoardText()
        {
            var sb = new StringBuilder(_world.Dead ? "GAME OVER – RANGLISTE\n\n" : "RANGLISTE (LIVE)\n\n");
            int n = 1;
            foreach (var row in _net.ScoreboardRows(_world.Score, !_world.Dead))
            {
                bool me = Json.Str(row, "id") == _net.LocalId;
                long score = me ? _world.Score : Json.Int(row, "score");
                sb.Append(n++).Append(". ").Append(Json.Str(row, "name")).Append("  –  ").Append(score).Append(me ? "  (du)" : "").Append(Json.Bool(row, "alive", true) ? "" : "  GAME OVER").Append('\n');
            }
            return sb.ToString();
        }
    }
}
