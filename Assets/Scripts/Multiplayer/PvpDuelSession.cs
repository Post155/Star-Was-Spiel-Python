using System;
using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class PvpDuelPlayer
    {
        public string Id; public string Name; public ShipDefinition Ship; public PlayerShipController Controller; public int Score; public bool Eliminated; public float RespawnAt;
    }

    public sealed class PvpDuelSession : MonoBehaviour
    {
        [SerializeField] private AssetLibrary assets;[SerializeField] private LocalInputRouter input;[SerializeField] private bool lastSurvivor=true;
        public PvpDuelPlayer Player1{get;private set;} public PvpDuelPlayer Player2{get;private set;}
        public bool MatchOver{get;private set;} public string WinnerId{get;private set;}
        private Dictionary<ShipId,ShipDefinition> _ships; private float _elapsed; private int _sequence;

        private void Start(){if(assets==null)assets=FindObjectOfType<AssetLibrary>();if(input==null)input=FindObjectOfType<LocalInputRouter>();_ships=RuntimeContent.BuildShips(assets);Player1=Create("local_p1","P1",ShipId.XWing,new Vector2(Screen.width*.35f,Screen.height-120));Player2=Create("local_p2","P2",ShipId.TieFighter,new Vector2(Screen.width*.55f,60));}
        private PvpDuelPlayer Create(string id,string name,ShipId ship,Vector2 pos){var go=new GameObject(name);var c=go.AddComponent<PlayerShipController>();c.Configure(_ships[ship]);c.ResetLives();c.ProjectileCreated+=p=>{};go.transform.position=PixelSpace.TopLeftToWorld(pos.x,pos.y,96,96);return new PvpDuelPlayer{Id=id,Name=name,Ship=_ships[ship],Controller=c};}

        private void Update(){if(MatchOver||Player1==null||Player2==null)return;_elapsed+=Time.deltaTime;var a=input!=null?input.ReadPlayer1():default;var b=input!=null?input.ReadPlayer2():default;Step(Player1,a);Step(Player2,b);if(lastSurvivor){if(Player1.Controller.Lives<=0){Player1.Eliminated=true;Finish(Player2.Id);}else if(Player2.Controller.Lives<=0){Player2.Eliminated=true;Finish(Player1.Id);}}else if(_elapsed>=GameConstants.PvPScoreLimitMs/1000f)Finish(Player1.Score>=Player2.Score?Player1.Id:Player2.Id);}
        private void Step(PvpDuelPlayer p,PlayerInputState inputState){if(p.Controller==null||p.Eliminated)return;p.Controller.Move(inputState.Move);if(inputState.Laser)p.Controller.FireLaser();if(inputState.Torpedo)p.Controller.FireTorpedo();}
        private void Finish(string winner){MatchOver=true;WinnerId=winner;_sequence++;}
    }
}
