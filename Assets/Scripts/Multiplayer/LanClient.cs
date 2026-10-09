using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class LanClient : IDisposable
    {
        private TcpClient _client; private StreamReader _reader; private StreamWriter _writer; private Thread _thread; private volatile bool _running;
        private readonly ConcurrentQueue<string> _incoming = new ConcurrentQueue<string>();
        public string PlayerId {get;private set;} public string HostId{get;private set;} public string Phase{get;private set;}="lobby"; public bool Connected=>_client!=null&&_client.Connected; public string Error{get;private set;}
        public event Action<string> MessageReceived;

        public void Connect(string host,int port,string name,string mode)
        {
            Disconnect(false);try{_client=new TcpClient();_client.Connect(host,port);_reader=new StreamReader(_client.GetStream(),Encoding.UTF8);_writer=new StreamWriter(_client.GetStream(),new UTF8Encoding(false)){AutoFlush=true};_running=true;
                Send(new NetMessage{type="hello",json=JsonUtility.ToJson(new HelloMessage{name=name,gameMode=mode})});_thread=new Thread(ReadLoop){IsBackground=true};_thread.Start();}catch(Exception ex){Error=ex.Message;Disconnect(false);}
        }

        private void ReadLoop(){try{string line;while(_running&&(line=_reader.ReadLine())!=null)_incoming.Enqueue(line);}catch{}finally{if(_running){_incoming.Enqueue(JsonUtility.ToJson(new NetMessage{type="server_stopped",json="Verbindung beendet"}));_running=false;}}}
        public void Pump(){while(_incoming.TryDequeue(out var line)){try{var e=JsonUtility.FromJson<NetMessage>(line);if(e==null)continue;if(e.type=="welcome"){var p=(e.json??"").Split('|');PlayerId=p.Length>0?p[0]:null;HostId=p.Length>1?p[1]:null;}else if(e.type=="snapshot"){var s=JsonUtility.FromJson<LobbyMessage>(e.json);Phase=s.phase;HostId=s.hostId;}else if(e.type=="countdown")Phase="countdown";else if(e.type=="game_started")Phase="game";else if(e.type=="server_stopped")Phase="stopped";MessageReceived?.Invoke(line);}catch{}}}
        public void Send(NetMessage message){if(!Connected)return;try{_writer.WriteLine(JsonUtility.ToJson(message));}catch{} }
        public void SendReady(string name,string ship,string difficulty,string rule)=>Send(new NetMessage{type="ready",json=JsonUtility.ToJson(new ReadyMessage{name=name,ship=ship,difficulty=difficulty,gameRule=rule})});
        public void SendState(StateMessage state){state.type="state";state.id=PlayerId;Send(new NetMessage{type="state",json=JsonUtility.ToJson(state)});}
        public void SendPointsState(PointsStateMessage state){state.type="points_state";state.id=PlayerId;Send(new NetMessage{type="points_state",json=JsonUtility.ToJson(state)});}
        public void SendPvpInput(bool left,bool right)=>Send(new NetMessage{type="pvp_input",json=JsonUtility.ToJson(new PvpInputMessage{type="pvp_input",id=PlayerId,left=left,right=right})});
        public void SendPvpFire(string weapon,int sequence)=>Send(new NetMessage{type="pvp_fire",json=JsonUtility.ToJson(new PvpFireMessage{type="pvp_fire",id=PlayerId,weapon=weapon,sequence=sequence})});
        public void RequestStart()=>Send(new NetMessage{type="start_request"});
        public void Disconnect(bool graceful=true){try{if(graceful)Send(new NetMessage{type="disconnect"});}catch{} _running=false;try{_client?.Close();}catch{} _client=null;_reader=null;_writer=null;PlayerId=null;HostId=null;Phase="lobby";}
        public void Dispose()=>Disconnect(false);
    }
}
