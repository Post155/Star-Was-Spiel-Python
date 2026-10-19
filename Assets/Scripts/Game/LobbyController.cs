using System.Text;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>
    /// LAN-Lobby: verbindet (Host erstellt den Server, sonst Beitritt per IP), zeigt Spielerliste und Bereitschaft,
    /// führt durch die Auswahl (Fraktion/Schwierigkeit/Schiff), zeigt den Countdown und lädt dann die LAN-Spielszene.
    /// </summary>
    public sealed class LobbyController : MonoBehaviour
    {
        private Text _title, _status, _list, _info, _big;
        private Button _start;
        private bool _leaving;

        private void Start()
        {
            if (AppState.Net == null)
            {
                bool points = AppState.Mode == GameMode.LanPoints;
                var s = new MultiplayerSession(points ? Msg.ModePoints : Msg.ModePvp, points ? GameConstants.MaxPlayers : GameConstants.PvpMaxPlayers);
                AppState.Net = s;
                try
                {
                    if (AppState.LanHosting) s.Host(AppState.LanName);
                    else s.Join(AppState.LanAddress, AppState.LanName);
                }
                catch (System.Exception ex) { s.Error = "Server konnte nicht gestartet werden: " + ex.Message; }
            }
            Build();
        }

        private void Build()
        {
            var canvas = Ui.CreateCanvas("LobbyCanvas", 1280, 720);
            var col = Ui.Column(canvas.transform, 760, 10);
            _title = Ui.Line(col, "LAN-LOBBY", 56, Ui.Gold, 70, FontStyle.Bold);
            _info = Ui.Line(col, "", 22, Ui.Grey, 60);
            _status = Ui.Line(col, "Verbinde …", 24, Color.white, 36);
            _list = Ui.Line(col, "", 26, Color.white, 220, FontStyle.Normal, TextAnchor.UpperLeft);
            _big = Ui.Line(col, "", 90, Ui.Gold, 100, FontStyle.Bold);
            _start = Ui.Btn(col, "START", () => AppState.Net.RequestStart(), 60, 28);
            Ui.Btn(col, "Verlassen", Leave, 52, 24);
        }

        private void Leave()
        {
            if (_leaving) return;
            _leaving = true;
            AppState.LeaveNetwork();
            SceneManager.LoadScene(SceneNames.MultiplayerMenu);
        }

        private void Update()
        {
            var net = AppState.Net;
            if (net == null || _leaving) return;
            net.Poll();

            bool pvp = net.GameMode == Msg.ModePvp;
            _title.text = "LAN-LOBBY – " + (pvp ? "Letzter Überlebender" : "Punktekampf");
            if (net.Hosting && net.Server != null)
            {
                var sb = new StringBuilder("Deine Adresse(n) für Mitspieler: ");
                foreach (var a in net.Server.GetLocalAddresses()) sb.Append(a).Append("  ");
                sb.Append("(Port ").Append(net.Server.Port).Append(")");
                _info.text = sb.ToString();
            }
            else _info.text = "Beitritt zu " + AppState.LanAddress;

            if (net.Client.HostDisconnected || (!net.Connected && !net.Connecting && net.LocalId == null && !string.IsNullOrEmpty(net.Error)))
            {
                _status.text = "Fehler: " + (net.Error ?? "Verbindung beendet.");
                _status.color = Ui.Danger; _start.gameObject.SetActive(false); return;
            }
            if (net.Connecting) { _status.text = "Verbinde …"; return; }
            if (!net.Connected && net.Phase != "game") { _status.text = "Verbindung getrennt."; _status.color = Ui.Danger; return; }

            var sbp = new StringBuilder();
            int n = 0;
            foreach (var id in net.Client.PlayerOrder)
            {
                if (!net.Players.TryGetValue(id, out var p)) continue; n++;
                sbp.Append(n).Append(". ").Append(Json.Str(p, "name", "?"));
                if (id == net.HostId) sbp.Append("  [HOST]");
                if (id == net.LocalId) sbp.Append("  (du)");
                if (Json.Bool(p, "ready")) sbp.Append("  [bereit]");
                sbp.Append('\n');
            }
            _list.text = sbp.ToString();
            int max = net.MaxPlayers;
            string phase = net.Phase;
            _big.text = "";
            _status.color = Color.white;
            if (phase == "lobby")
            {
                _status.text = $"Verbunden: {n} / {max}";
                bool canStart = net.IsHost && (pvp ? n == GameConstants.PvpMaxPlayers : n >= 1);
                _start.gameObject.SetActive(net.IsHost);
                _start.interactable = canStart;
                if (net.IsHost && pvp && n < 2) _status.text += "  –  warte auf den zweiten Spieler";
                if (!net.IsHost) _status.text += "  –  warte auf den Start durch den Host";
            }
            else if (phase == "setup")
            {
                _start.gameObject.SetActive(false);
                bool ready = net.LocalId != null && net.Players.TryGetValue(net.LocalId, out var me) && Json.Bool(me, "ready");
                if (!ready) { SceneManager.LoadScene(SceneNames.Faction); _leaving = true; return; }   // Auswahl durchlaufen, danach zurück
                _status.text = "Bereit – warte auf die anderen Spieler …";
            }
            else if (phase == "countdown")
            {
                _start.gameObject.SetActive(false);
                _status.text = "Das Spiel startet!";
                _big.text = Mathf.Max(1, Mathf.CeilToInt((float)net.Client.CountdownLeftMs / 1000f)).ToString();
            }
            else if (phase == "game") { _leaving = true; SceneManager.LoadScene(SceneNames.LanGame); }
        }
    }
}
