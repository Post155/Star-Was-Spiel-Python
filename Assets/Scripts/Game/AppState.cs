using System;
using UnityEngine;
using StarWars.Sim;

namespace StarWars.Game
{
    public enum GameMode { Single, LocalPoints, LocalLastSurvivor, LanPoints, LanLastSurvivor }

    public static class SceneNames
    {
        public const string MainMenu = "MainMenu", Faction = "FactionSelection", Difficulty = "DifficultySelection", Ship = "ShipSelection",
            Singleplayer = "Singleplayer", MultiplayerMenu = "MultiplayerMenu", LocalPointsFight = "LocalPointsFight",
            LocalLastSurvivor = "LocalLastSurvivor", LanLobby = "LanLobby", LanGame = "LanGame";
        public static readonly string[] All = { MainMenu, Faction, Difficulty, Ship, Singleplayer, MultiplayerMenu, LocalPointsFight, LocalLastSurvivor, LanLobby, LanGame };
    }

    public sealed class PlayerSetup
    {
        public string Name = "Spieler";
        public string Faction = "rebels";
        public string Ship = "xwing";
        public string Difficulty = "normal";
    }

    /// <summary>Gemeinsamer Zustand zwischen den Szenen (Auswahl, Dienste, laufende LAN-Sitzung) und die Menü-Ablauflogik.</summary>
    public static class AppState
    {
        public static GameMode Mode = GameMode.Single;
        public static readonly PlayerSetup[] Players = { new PlayerSetup { Name = GameConstants.LocalPlayer1Name }, new PlayerSetup { Name = GameConstants.LocalPlayer2Name } };
        public static int SetupIndex;                         // welcher lokale Spieler gerade wählt
        public static string LanName = "Spieler", LanAddress = "127.0.0.1";
        public static bool LanHosting;
        public static string LanRule = PvpModes.LastSurvivor;
        public static MultiplayerSession Net;                 // aktive LAN-Sitzung (szenenübergreifend)

        // ---- Dienste ----
        private static SaveService _save;
        public static ItemDatabase Items { get; private set; }
        public static Inventory Inventory { get; private set; }
        public static QuestLog Quests { get; private set; }
        public static SaveService Save { get { EnsureServices(); return _save; } }

        public static void EnsureServices()
        {
            if (_save != null) return;
            _save = new SaveService(Application.persistentDataPath);
            _save.Load();
            Items = ContentLoader.LoadItems();
            Inventory = new Inventory(Items, 12);
            Quests = QuestLog.CreateDefault();
            Inventory.LoadJson(_save.Data.Inventory);
            Quests.LoadJson(_save.Data.Quests);
            var s = _save.Data.Settings;
            Players[0].Ship = s.LastShip; Players[0].Faction = s.LastFaction; Players[0].Difficulty = s.LastDifficulty;
            LanName = s.PlayerName;
            AudioListener.volume = (float)s.MasterVolume;
        }

        /// <summary>Inventar und Quests in den Spielstand übernehmen und schreiben.</summary>
        public static void PersistProgress()
        {
            EnsureServices();
            _save.Data.Inventory = Inventory.ToJson();
            _save.Data.Quests = Quests.ToJson();
            _save.Save();
        }

        public static void RememberSelection()
        {
            EnsureServices();
            var p = Players[0];
            _save.Data.Settings.LastShip = p.Ship; _save.Data.Settings.LastFaction = p.Faction; _save.Data.Settings.LastDifficulty = p.Difficulty;
            _save.Data.Settings.PlayerName = Proto.SafeName(LanName);
            _save.Save();
        }

        public static PlayerSetup CurrentSetup => Players[Mode == GameMode.Single || IsLan ? 0 : Math.Min(1, SetupIndex)];
        public static bool IsLan => Mode == GameMode.LanPoints || Mode == GameMode.LanLastSurvivor;
        public static bool IsLocalVersus => Mode == GameMode.LocalPoints || Mode == GameMode.LocalLastSurvivor;
        public static bool UsesDifficulty => Mode == GameMode.Single || Mode == GameMode.LocalPoints || Mode == GameMode.LanPoints;

        public static void ResetSelections()
        {
            Players[0].Name = GameConstants.LocalPlayer1Name; Players[1].Name = GameConstants.LocalPlayer2Name;
            Players[1].Ship = "tiefighter"; Players[1].Faction = "empire";
            SetupIndex = 0;
        }

        // ---- Ablauf (entspricht den Flows in StarWarsGame.py) ----
        public static string AfterFaction() => UsesDifficulty ? SceneNames.Difficulty : SceneNames.Ship;
        public static string AfterDifficulty() => SceneNames.Ship;

        public static string AfterShip()
        {
            switch (Mode)
            {
                case GameMode.Single: RememberSelection(); return SceneNames.Singleplayer;
                case GameMode.LocalPoints:
                case GameMode.LocalLastSurvivor:
                    if (SetupIndex == 0) { SetupIndex = 1; return SceneNames.Faction; }
                    return Mode == GameMode.LocalPoints ? SceneNames.LocalPointsFight : SceneNames.LocalLastSurvivor;
                default:   // LAN: Auswahl abschicken, zurück in die Lobby (Warten auf Countdown)
                    RememberSelection();
                    if (Net != null) Net.SendReady(Players[0].Ship, Players[0].Difficulty, Mode == GameMode.LanLastSurvivor ? LanRule : null);
                    return SceneNames.LanLobby;
            }
        }

        public static void LeaveNetwork()
        {
            if (Net != null) { Net.Stop(true); Net = null; }
        }
    }
}
