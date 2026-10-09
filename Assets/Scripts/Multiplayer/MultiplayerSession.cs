using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class MultiplayerSession : MonoBehaviour
    {
        [SerializeField] private int port=28000;
        public LanServer Server {get;private set;} public LanClient Client {get;private set;} public bool IsHost {get;private set;}
        public readonly Dictionary<string,PlayerLobbyData> Players=new Dictionary<string,PlayerLobbyData>();

        public void Host(string name,string mode){Stop();IsHost=true;Server=new LanServer(port,mode,2);Server.Start();Client=new LanClient();Client.Connect("127.0.0.1",port,name,mode);}
        public void Join(string host,string name,string mode){Stop();IsHost=false;Client=new LanClient();Client.Connect(host,port,name,mode);}
        public void Update()
        {
            Server?.Pump(); Client?.Pump();
        }
        public void SendReady(string name,string ship,string difficulty,string rule){Client?.SendReady(name,ship,difficulty,rule);}
        public void SendState(PlayerShipController player,string ship,int score,string system)
        {
            if(Client==null||player==null)return;
            Client.SendState(new StateMessage{x=player.PixelPosition.x,y=player.PixelPosition.y,width=Screen.width,height=Screen.height,ship=ship,score=score,lives=player.Lives,alive=player.Lives>0,system=system});
        }
        public void SendPointsState(PlayerShipController player,string ship,int score,string system)
        {
            if(Client==null||player==null)return;
            Client.SendPointsState(new PointsStateMessage{x=player.PixelPosition.x/Mathf.Max(1,Screen.width),y=player.PixelPosition.y/Mathf.Max(1,Screen.height),ship=ship,score=score,system=system});
        }
        public void SendPvpInput(bool left,bool right)=>Client?.SendPvpInput(left,right);
        public void SendPvpFire(string weapon,int sequence)=>Client?.SendPvpFire(weapon,sequence);
        public void Stop(){Client?.Dispose();Server?.Dispose();Client=null;Server=null;Players.Clear();}
        private void OnDestroy()=>Stop();
    }
}
