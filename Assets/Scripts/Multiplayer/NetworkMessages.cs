using System;

namespace StarWarsUnity
{
    [Serializable] public sealed class NetMessage { public string type; public string json; }
    [Serializable] public sealed class HelloMessage { public string type="hello"; public string version="1"; public string name; public string gameMode="lan"; }
    [Serializable] public sealed class ReadyMessage { public string type="ready"; public string name; public string ship; public string difficulty; public string gameRule; }
    [Serializable] public sealed class StateMessage { public string type="state"; public string id; public string name; public string ship; public float x; public float y; public int width; public int height; public int score; public int lives; public bool alive; public string system; }
    [Serializable] public sealed class PointsStateMessage { public string type="points_state"; public string id; public string name; public string ship; public float x; public float y; public int score; public string system; }
    [Serializable] public sealed class PvpInputMessage { public string type="pvp_input"; public string id; public bool left; public bool right; }
    [Serializable] public sealed class PvpFireMessage { public string type="pvp_fire"; public string id; public string weapon; public int sequence; }
    [Serializable] public sealed class LobbyMessage { public string type="snapshot"; public string phase; public string hostId; public PlayerLobbyData[] players; public int maxPlayers; }
    [Serializable] public sealed class PlayerLobbyData { public string id; public string name; public string ship; public string difficulty; public string gameRule; public bool ready; public int score; public bool alive=true; public int lives=3; public string system; public float x; public float y; }
    [Serializable] public sealed class CountdownMessage { public string type="countdown"; public double startedAt; }
    [Serializable] public sealed class PvpSnapshotMessage { public string type="pvp_snapshot"; public double serverTime; public int systemIndex; public float matchElapsed; public PvpNetPlayer[] players; public PvpNetProjectile[] projectiles; }
    [Serializable] public sealed class PvpNetPlayer { public string id; public string name; public string ship; public float x; public float y; public int lives; public int score; public bool eliminated; public float respawnAt; }
    [Serializable] public sealed class PvpNetProjectile { public int id; public string ownerId; public string weapon; public float x; public float y; public float vx; public float vy; }
}
