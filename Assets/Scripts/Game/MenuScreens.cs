using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using StarWars.Sim;

namespace StarWars.Game
{
    /// <summary>Alle klassischen Menüs: Hauptmenü, Fraktion, Schwierigkeit, Schiff, Mehrspieler-Menü (+ Quests/Inventar).</summary>
    public sealed class MenuScreens : MonoBehaviour
    {
        private Canvas _canvas;
        private RectTransform _col;
        private string _scene;
        private Text _status;
        private int _stage;                       // MultiplayerMenu: 0 = Modus, 1 = Regel, 2 = LAN-Formular
        private bool _lan;
        private InputField _nameField, _ipField;

        private static void Load(string scene) { SceneManager.LoadScene(scene); }

        private void Start()
        {
            _scene = SceneManager.GetActiveScene().name;
            Rebuild();
        }

        private void Rebuild()
        {
            if (_canvas != null) Destroy(_canvas.gameObject);
            _canvas = Ui.CreateCanvas("MenuCanvas", 1280, 720);
            _col = Ui.Column(_canvas.transform, 640, 14);
            switch (_scene)
            {
                case SceneNames.Faction: BuildFaction(); break;
                case SceneNames.Difficulty: BuildDifficulty(); break;
                case SceneNames.Ship: BuildShip(); break;
                case SceneNames.MultiplayerMenu: BuildMultiplayer(); break;
                default: BuildMain(); break;
            }
        }

        private void Update()
        {
            foreach (var k in _keyBindings) if (InputAccumulator.KeyDown(k.Key)) { k.Value(); break; }
        }

        private readonly Dictionary<KeyCode, System.Action> _keyBindings = new Dictionary<KeyCode, System.Action>();
        private void Bind(KeyCode key, System.Action a) { _keyBindings[key] = a; }
        private void ClearBindings() { _keyBindings.Clear(); }

        private string PlayerHeader()
        {
            if (AppState.IsLocalVersus) return $"{AppState.Players[AppState.SetupIndex].Name}  –  " + (AppState.SetupIndex == 0 ? "A / D = Bewegen   W = Laser   S = Torpedo" : "← / → = Bewegen   ↑ = Laser   ↓ = Torpedo");
            return "";
        }

        // ------------------------------------------------------------------ Hauptmenü
        private void BuildMain()
        {
            ClearBindings();
            Ui.Line(_col, "STAR WARS", 76, Ui.Gold, 110, FontStyle.Bold);
            Ui.Line(_col, "Rekord: " + AppState.Save.Data.Highscore, 26, Ui.Grey, 36);
            Ui.Spacer(_col, 14);
            Ui.Btn(_col, "Einzelspieler  [1]", StartSingle);
            Ui.Btn(_col, "Mehrspieler  [2]", () => Load(SceneNames.MultiplayerMenu));
            Ui.Btn(_col, "Quests & Inventar  [3]", ShowProgression);
            Ui.Btn(_col, "Beenden  [Esc]", Quit);
            Bind(KeyCode.Alpha1, StartSingle); Bind(KeyCode.Keypad1, StartSingle);
            Bind(KeyCode.Alpha2, () => Load(SceneNames.MultiplayerMenu)); Bind(KeyCode.Keypad2, () => Load(SceneNames.MultiplayerMenu));
            Bind(KeyCode.Alpha3, ShowProgression);
            Bind(KeyCode.Escape, Quit);
            Ui.Spacer(_col, 10);
            Ui.Line(_col, "Steuerung: A/D oder ←/→ bewegen · Leertaste/W/↑ Laser · S/↓ Torpedo · H Hitboxen · 1–4 Schiff wechseln (Debug)", 17, Ui.Grey, 44);
        }

        private void StartSingle()
        {
            AppState.Mode = GameMode.Single; AppState.ResetSelections(); AppState.LeaveNetwork(); Load(SceneNames.Faction);
        }

        private void Quit()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        private void ShowProgression()
        {
            ClearBindings();
            Destroy(_col.gameObject); _col = Ui.Column(_canvas.transform, 900, 8);
            Ui.Line(_col, "QUESTS & INVENTAR", 44, Ui.Gold, 60, FontStyle.Bold);
            Ui.Line(_col, "Fortschritt zählt in jeder Einzelspielerrunde (Asteroiden, Gegner, Punkte, Systeme).", 18, Ui.Grey, 28);
            foreach (var def in AppState.Quests.Definitions)
            {
                var prog = AppState.Quests.GetProgress(def.Id);
                var row = new GameObject("Quest", typeof(RectTransform)); row.transform.SetParent(_col, false);
                var le = row.AddComponent<LayoutElement>(); le.preferredHeight = 54; le.minHeight = 54;
                var h = row.AddComponent<HorizontalLayoutGroup>(); h.childAlignment = TextAnchor.MiddleLeft; h.spacing = 12; h.childControlWidth = true; h.childControlHeight = true; h.childForceExpandWidth = false; h.childForceExpandHeight = true;
                var txt = Ui.Label(row.transform, $"{def.Title} – {def.Description}\n{prog.State}  {prog.Progress}/{def.Target}   Belohnung: {RewardText(def)}", 18, TextAnchor.MiddleLeft);
                var tle = txt.gameObject.AddComponent<LayoutElement>(); tle.flexibleWidth = 1;
                string id = def.Id;
                if (prog.State == QuestState.Available) { var b = Ui.MakeButton(row.transform, "Annehmen", () => { AppState.Quests.Accept(id); AppState.PersistProgress(); ShowProgression(); }, "Accept", 20); b.gameObject.AddComponent<LayoutElement>().preferredWidth = 170; }
                else if (prog.State == QuestState.Completed) { var b = Ui.MakeButton(row.transform, "Abholen", () => { if (!AppState.Quests.Claim(id, AppState.Inventory)) Debug.Log("Inventar voll – Belohnung bleibt abholbar."); AppState.PersistProgress(); ShowProgression(); }, "Claim", 20); b.gameObject.AddComponent<LayoutElement>().preferredWidth = 170; }
            }
            Ui.Spacer(_col, 8);
            var sb = new StringBuilder("Inventar (" + (AppState.Inventory.SlotCount - AppState.Inventory.FreeSlots()) + "/" + AppState.Inventory.SlotCount + " Plätze):\n");
            bool any = false;
            for (int i = 0; i < AppState.Inventory.SlotCount; i++)
            {
                var s = AppState.Inventory.GetSlot(i); if (s.IsEmpty) continue;
                var d = AppState.Items.Get(s.ItemId); sb.Append("• ").Append(d != null ? d.Name : s.ItemId).Append(" × ").Append(s.Count).Append("   ");
                any = true;
            }
            if (!any) sb.Append("(leer)");
            Ui.Line(_col, sb.ToString(), 20, Color.white, 90);
            Ui.Btn(_col, "Zurück  [Esc]", () => { Load(SceneNames.MainMenu); }, 50, 24);
            Bind(KeyCode.Escape, () => Load(SceneNames.MainMenu));
        }

        private static string RewardText(QuestDefinition d)
        {
            var item = AppState.Items.Get(d.RewardItemId);
            return (item != null ? item.Name : d.RewardItemId) + " ×" + d.RewardCount;
        }

        // ------------------------------------------------------------------ Fraktion
        private void BuildFaction()
        {
            ClearBindings();
            Ui.Line(_col, "WÄHLE DEINE SEITE", 52, Ui.Gold, 70, FontStyle.Bold);
            if (AppState.IsLocalVersus) Ui.Line(_col, PlayerHeader(), 20, Ui.Grey, 30);
            Ui.Spacer(_col, 6);
            var row = new GameObject("Row", typeof(RectTransform)); row.transform.SetParent(_col, false);
            row.AddComponent<LayoutElement>().preferredHeight = 330;
            var h = row.AddComponent<HorizontalLayoutGroup>(); h.spacing = 24; h.childControlWidth = true; h.childControlHeight = true; h.childForceExpandWidth = true; h.childForceExpandHeight = true;
            FactionCard(row.transform, "Rebellen  [1]", SpriteLibrary.RebelLogo, "rebels");
            FactionCard(row.transform, "Imperium  [2]", SpriteLibrary.EmpireLogo, "empire");
            Ui.Btn(_col, "Zurück  [Esc]", Back, 48, 22);
            Bind(KeyCode.Alpha1, () => PickFaction("rebels")); Bind(KeyCode.Alpha2, () => PickFaction("empire"));
            Bind(KeyCode.LeftArrow, () => PickFaction("rebels")); Bind(KeyCode.RightArrow, () => PickFaction("empire"));
            Bind(KeyCode.Escape, Back);
        }

        private void FactionCard(Transform parent, string label, Sprite logo, string key)
        {
            var b = Ui.MakeButton(parent, "", () => PickFaction(key), "Faction_" + key);
            foreach (Transform c in b.transform) Destroy(c.gameObject);
            var img = Ui.Rect(b.transform, "Logo", new Vector2(0.05f, 0.25f), new Vector2(0.95f, 0.95f), Vector2.zero, Vector2.zero).gameObject.AddComponent<Image>();
            img.sprite = logo; img.preserveAspect = true; img.raycastTarget = false;
            Ui.LabelAt(b.transform, label, new Vector2(0, 0), new Vector2(1, 0.25f), 28, TextAnchor.MiddleCenter, Color.white, FontStyle.Bold);
        }

        private void PickFaction(string key)
        {
            var p = AppState.CurrentSetup; p.Faction = key;
            p.Ship = key == "rebels" ? "xwing" : "tiefighter";
            Load(AppState.AfterFaction());
        }

        private void Back()
        {
            if (AppState.IsLocalVersus && AppState.SetupIndex == 1) { AppState.SetupIndex = 0; Load(SceneNames.Ship); return; }
            if (AppState.IsLan) { Load(SceneNames.LanLobby); return; }
            Load(AppState.IsLocalVersus ? SceneNames.MultiplayerMenu : SceneNames.MainMenu);
        }

        // ------------------------------------------------------------------ Schwierigkeit
        private void BuildDifficulty()
        {
            ClearBindings();
            Ui.Line(_col, "SCHWIERIGKEITSGRAD", 52, Ui.Gold, 70, FontStyle.Bold);
            if (AppState.IsLocalVersus) Ui.Line(_col, AppState.Players[AppState.SetupIndex].Name, 22, Ui.Grey, 30);
            int i = 1;
            foreach (var key in Difficulties.Keys)
            {
                var d = Difficulties.Get(key); string k = key;
                Ui.Btn(_col, $"{d.Name}  [{i}]\n{d.Description}", () => PickDifficulty(k), 78, 24);
                int idx = i; Bind((KeyCode)((int)KeyCode.Alpha0 + idx), () => PickDifficulty(k)); Bind((KeyCode)((int)KeyCode.Keypad0 + idx), () => PickDifficulty(k));
                i++;
            }
            Ui.Btn(_col, "Zurück  [Esc]", () => Load(SceneNames.Faction), 48, 22);
            Bind(KeyCode.Escape, () => Load(SceneNames.Faction));
        }

        private void PickDifficulty(string key) { AppState.CurrentSetup.Difficulty = key; Load(AppState.AfterDifficulty()); }

        // ------------------------------------------------------------------ Schiff
        private void BuildShip()
        {
            ClearBindings();
            var setup = AppState.CurrentSetup;
            var faction = setup.Faction == "empire" ? Faction.Empire : Faction.Rebels;
            Ui.Line(_col, "WÄHLE DEIN SCHIFF", 52, Ui.Gold, 70, FontStyle.Bold);
            if (AppState.IsLocalVersus) Ui.Line(_col, PlayerHeader(), 20, Ui.Grey, 30);
            var row = new GameObject("Row", typeof(RectTransform)); row.transform.SetParent(_col, false);
            row.AddComponent<LayoutElement>().preferredHeight = 340;
            var h = row.AddComponent<HorizontalLayoutGroup>(); h.spacing = 24; h.childControlWidth = true; h.childControlHeight = true; h.childForceExpandWidth = true; h.childForceExpandHeight = true;
            int i = 1;
            foreach (var ship in ShipCatalog.ForFaction(faction))
            {
                var s = ship; var b = Ui.MakeButton(row.transform, "", () => PickShip(s.Key), "Ship_" + s.Key);
                foreach (Transform c in b.transform) Destroy(c.gameObject);
                var img = Ui.Rect(b.transform, "Preview", new Vector2(0.08f, 0.38f), new Vector2(0.92f, 0.95f), Vector2.zero, Vector2.zero).gameObject.AddComponent<Image>();
                img.sprite = SpriteLibrary.Ship(s.Key); img.preserveAspect = true; img.raycastTarget = false;
                if (s.Key == "tiefighter") img.transform.localRotation = Quaternion.Euler(0, 0, 180);
                Ui.LabelAt(b.transform, $"{s.DisplayName}  [{i}]", new Vector2(0, 0.22f), new Vector2(1, 0.36f), 26, TextAnchor.MiddleCenter, Color.white, FontStyle.Bold);
                Ui.LabelAt(b.transform, $"Tempo {s.Speed}   Torpedos: {(s.HasTorpedo ? "ja" : "nein")}", new Vector2(0, 0.04f), new Vector2(1, 0.2f), 20, TextAnchor.MiddleCenter, Ui.Grey);
                Bind((KeyCode)((int)KeyCode.Alpha0 + i), () => PickShip(s.Key)); Bind((KeyCode)((int)KeyCode.Keypad0 + i), () => PickShip(s.Key));
                i++;
            }
            Ui.Btn(_col, "Zurück  [Esc]", () => Load(AppState.UsesDifficulty ? SceneNames.Difficulty : SceneNames.Faction), 48, 22);
            Bind(KeyCode.Escape, () => Load(AppState.UsesDifficulty ? SceneNames.Difficulty : SceneNames.Faction));
        }

        private void PickShip(string key) { AppState.CurrentSetup.Ship = key; Load(AppState.AfterShip()); }

        // ------------------------------------------------------------------ Mehrspieler
        private void BuildMultiplayer()
        {
            ClearBindings();
            Ui.Line(_col, "MEHRSPIELER", 56, Ui.Gold, 80, FontStyle.Bold);
            if (_stage == 0)
            {
                Ui.Btn(_col, "Lokaler Multiplayer  [1]", () => { _lan = false; _stage = 1; Rebuild(); }, 62);
                Ui.Btn(_col, "LAN Multiplayer  [2]", () => { _lan = true; _stage = 1; Rebuild(); }, 62);
                Ui.Btn(_col, "Zurück  [Esc]", () => Load(SceneNames.MainMenu), 50, 22);
                Bind(KeyCode.Alpha1, () => { _lan = false; _stage = 1; Rebuild(); }); Bind(KeyCode.Alpha2, () => { _lan = true; _stage = 1; Rebuild(); });
                Bind(KeyCode.Escape, () => Load(SceneNames.MainMenu));
            }
            else if (_stage == 1)
            {
                Ui.Line(_col, _lan ? "LAN – Spielmodus" : "Lokal – Spielmodus", 26, Ui.Grey, 36);
                Ui.Btn(_col, "Letzter Überlebender  [1]\nDirektes Duell: Wer zuletzt steht, gewinnt", () => PickRule(PvpModes.LastSurvivor), 82, 22);
                Ui.Btn(_col, "Punktekampf  [2]\nZwei getrennte Welten – wer nach 3 Minuten mehr Punkte hat", () => PickRule(PvpModes.Points), 82, 22);
                Ui.Btn(_col, "Zurück  [Esc]", () => { _stage = 0; Rebuild(); }, 50, 22);
                Bind(KeyCode.Alpha1, () => PickRule(PvpModes.LastSurvivor)); Bind(KeyCode.Alpha2, () => PickRule(PvpModes.Points));
                Bind(KeyCode.Escape, () => { _stage = 0; Rebuild(); });
            }
            else
            {
                Ui.Line(_col, "LAN-Spiel  –  " + (AppState.LanRule == PvpModes.Points ? "Punktekampf (bis 10 Spieler)" : "Letzter Überlebender (2 Spieler)"), 24, Ui.Grey, 36);
                Ui.Line(_col, "Dein Name", 20, Ui.Grey, 26, FontStyle.Normal, TextAnchor.MiddleLeft);
                _nameField = Ui.MakeInput(_col, AppState.LanName, "Name", GameConstants.MaxNameLength); Ui.Sized(_nameField, 46);
                Ui.Line(_col, "Host-IP-Adresse (zum Beitreten)", 20, Ui.Grey, 26, FontStyle.Normal, TextAnchor.MiddleLeft);
                _ipField = Ui.MakeInput(_col, AppState.LanAddress, "z. B. 192.168.0.12", 40, true); Ui.Sized(_ipField, 46);
                Ui.Btn(_col, "Host erstellen", () => StartLan(true), 56, 24);
                Ui.Btn(_col, "Beitreten", () => StartLan(false), 56, 24);
                _status = Ui.Line(_col, "", 20, Ui.Danger, 30);
                Ui.Btn(_col, "Zurück  [Esc]", () => { _stage = 1; Rebuild(); }, 48, 22);
                Bind(KeyCode.Escape, () => { _stage = 1; Rebuild(); });
            }
        }

        private void PickRule(string rule)
        {
            AppState.LanRule = rule;
            if (_lan) { _stage = 2; Rebuild(); return; }
            AppState.Mode = rule == PvpModes.Points ? GameMode.LocalPoints : GameMode.LocalLastSurvivor;
            AppState.ResetSelections(); AppState.LeaveNetwork();
            Load(SceneNames.Faction);
        }

        private void StartLan(bool host)
        {
            string name = Proto.SafeName(_nameField.text);
            string ip = (_ipField.text ?? "").Trim();
            if (!host && ip.Length < 7) { _status.text = "Bitte eine gültige IP-Adresse eingeben."; return; }
            AppState.LanName = name; AppState.LanAddress = ip.Length > 0 ? ip : "127.0.0.1"; AppState.LanHosting = host;
            AppState.Mode = AppState.LanRule == PvpModes.Points ? GameMode.LanPoints : GameMode.LanLastSurvivor;
            AppState.ResetSelections(); AppState.LeaveNetwork(); AppState.RememberSelection();
            Load(SceneNames.LanLobby);
        }
    }
}
