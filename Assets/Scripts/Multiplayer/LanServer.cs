using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class LanServer : IDisposable
    {
        private sealed class Peer
        {
            public string Id; public string Name; public TcpClient Client; public StreamReader Reader; public StreamWriter Writer; public Thread Thread; public bool Ready;
        }

        private readonly object _gate = new object();
        private readonly Dictionary<string,Peer> _peers = new Dictionary<string,Peer>();
        private readonly ConcurrentQueue<(string id,string line)> _incoming = new ConcurrentQueue<(string,string)>();
        private readonly int _port; private readonly string _mode; private readonly int _maxPlayers;
        private TcpListener _listener; private Thread _acceptThread; private volatile bool _running;
        public string HostId { get; private set; }
        public string Phase { get; private set; } = "lobby";
        public event Action<string> MessageReceived;

        public LanServer(int port=28000,string mode="pvp",int maxPlayers=2){_port=port;_mode=mode;_maxPlayers=maxPlayers;}
        public void Start(){ if(_running)return; _running=true; _listener=new TcpListener(IPAddress.Any,_port);_listener.Start();_acceptThread=new Thread(AcceptLoop){IsBackground=true};_acceptThread.Start(); }

        private void AcceptLoop()
        {
            while(_running)
            {
                try { var client=_listener.AcceptTcpClient(); HandleClient(client); } catch { if(_running) Thread.Sleep(20); }
            }
        }

        private void HandleClient(TcpClient client)
        {
            string id=Guid.NewGuid().ToString("N");
            var peer=new Peer{Id=id,Client=client,Reader=new StreamReader(client.GetStream(),Encoding.UTF8),Writer=new StreamWriter(client.GetStream(),new UTF8Encoding(false)){AutoFlush=true}};
            lock(_gate){if(_peers.Count>=_maxPlayers){Send(peer,new NetMessage{type="error",json="Server voll"});client.Close();return;}_peers[id]=peer;if(string.IsNullOrEmpty(HostId))HostId=id;}
            peer.Thread=new Thread(()=>ReceiveLoop(peer)){IsBackground=true};peer.Thread.Start();
            Send(peer,new NetMessage{type="welcome",json=id+"|"+HostId}); BroadcastLobby();
        }

        private void ReceiveLoop(Peer peer)
        {
            try{string line;while(_running && peer.Client.Connected && (line=peer.Reader.ReadLine())!=null){_incoming.Enqueue((peer.Id,line));}}catch{} finally{RemovePeer(peer.Id);}
        }

        public void Pump()
        {
            while(_incoming.TryDequeue(out var item))
            {
                string id=item.id; string line=item.line;
                NetMessage envelope;
                try{envelope=JsonUtility.FromJson<NetMessage>(line);}catch{continue;}
                if(envelope==null)continue;
                Process(id,envelope);
                MessageReceived?.Invoke(item.line);
            }
        }

        private void Process(string id, NetMessage envelope)
        {
            switch(envelope.type)
            {
                case "hello":
                    break;
                case "ready": SetReady(id,envelope.json); break;
                case "state": RelayToOthers(id,envelope.json,"state"); break;
                case "points_state": RelayToOthers(id,envelope.json,"points_state"); break;
                case "pvp_input": RelayPvpInput(id,envelope.json); break;
                case "pvp_fire": RelayPvpFire(id,envelope.json); break;
                case "disconnect": RemovePeer(id); break;
                case "start_request": StartWhenReady(); break;
                case "pvp_snapshot": Broadcast(envelope); break;
            }
        }

        private void SetReady(string id,string payload)
        {
            lock(_gate){if(_peers.TryGetValue(id,out var p)) { p.Ready=true; try { var r=JsonUtility.FromJson<ReadyMessage>(payload); if(r!=null) p.Name=r.name; } catch{} }}
            RelayToOthers(id,payload,"ready"); BroadcastLobby(); StartWhenReady();
        }

        private void RelayPvpInput(string id,string payload)
        {
            try { var data=JsonUtility.FromJson<PvpInputMessage>(payload); data.id=id; payload=JsonUtility.ToJson(data); } catch{}
            RelayToHostOrAll(id,payload,"pvp_input");
        }

        private void RelayPvpFire(string id,string payload)
        {
            try { var data=JsonUtility.FromJson<PvpFireMessage>(payload); data.id=id; payload=JsonUtility.ToJson(data); } catch{}
            RelayToHostOrAll(id,payload,"pvp_fire");
        }

        private void StartWhenReady()
        {
            bool start;
            lock(_gate) start=_peers.Count==_maxPlayers && _peers.Values.All(p=>p.Ready);
            if(!start)return;
            Phase="countdown"; Broadcast(new NetMessage{type="countdown",json=JsonUtility.ToJson(new CountdownMessage{startedAt=DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()/1000.0+3.0})});
            ThreadPool.QueueUserWorkItem(_=>{Thread.Sleep(3000);if(_running){Phase="game";Broadcast(new NetMessage{type="game_started"});}});
        }

        public void Broadcast(NetMessage message)
        {
            string line=JsonUtility.ToJson(message);List<Peer> peers;
            lock(_gate)peers=_peers.Values.ToList();foreach(var p in peers)SendLine(p,line);
        }
        private void RelayToOthers(string senderId,string payload,string type){Broadcast(new NetMessage{type=type,json=payload});}
        private void RelayToHostOrAll(string senderId,string payload,string type){Broadcast(new NetMessage{type=type,json=payload});}
        private void BroadcastLobby(){var msg=BuildLobby();Broadcast(msg);}

        private NetMessage BuildLobby()
        {
            var data=new LobbyMessage{type="snapshot",phase=Phase,hostId=HostId,maxPlayers=_maxPlayers};
            lock(_gate){data.players=_peers.Values.Select(p=>new PlayerLobbyData{id=p.Id,name=string.IsNullOrWhiteSpace(p.Name)?"Spieler":p.Name,ready=p.Ready}).ToArray();}
            return new NetMessage{type="snapshot",json=JsonUtility.ToJson(data)};
        }

        private void Send(Peer peer,NetMessage message)=>SendLine(peer,JsonUtility.ToJson(message));
        private void SendLine(Peer peer,string line){try{peer.Writer.WriteLine(line);}catch{} }

        private void RemovePeer(string id)
        {
            Peer p=null;bool wasHost=false;lock(_gate){if(!_peers.TryGetValue(id,out p))return;wasHost=id==HostId;_peers.Remove(id);if(wasHost)HostId=_peers.Keys.FirstOrDefault();}
            try{p.Client.Close();}catch{};if(wasHost&&_running)Broadcast(new NetMessage{type="server_stopped",json="Host beendet"});else BroadcastLobby();
        }

        public void Dispose(){_running=false;try{_listener?.Stop();}catch{};lock(_gate){foreach(var p in _peers.Values){try{p.Client.Close();}catch{}}_peers.Clear();}}
    }
}
