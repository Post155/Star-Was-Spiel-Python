using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class PointsFightWorld
    {
        public readonly string Name; public readonly Faction Faction; public readonly ShipDefinition Ship;
        public PlayerShipController Player {get;private set;} public int Score {get;private set;} public bool Dead=>Player==null||Player.Lives<=0;
        public string SystemName=>_background!=null?_background.CurrentSystemName:"";
        private readonly AssetLibrary _assets; private readonly BackgroundManager _background; private readonly EnemyManager _enemies;
        private readonly List<AsteroidController> _asteroids=new List<AsteroidController>(); private readonly List<ProjectileController> _projectiles=new List<ProjectileController>();
        private float _spawnTimer;

        public PointsFightWorld(string name,Faction faction,ShipDefinition ship,AssetLibrary assets)
        {
            Name=name;Faction=faction;Ship=ship;_assets=assets;
            var go=new GameObject($"PointsWorld_{name}");
            var bgGo=new GameObject($"Background_{name}");_background=bgGo.AddComponent<BackgroundManager>();var sys=bgGo.AddComponent<StarSystemManager>();var stars=bgGo.AddComponent<StarfieldController>();
            _background.Initialize(assets);
            var enemyGo=new GameObject($"Enemies_{name}");_enemies=enemyGo.AddComponent<EnemyManager>();
            var pgo=new GameObject($"Player_{name}");Player=pgo.AddComponent<PlayerShipController>();Player.Configure(ship);Player.ProjectileCreated+=p=>_projectiles.Add(p);Player.Died+=()=>{};
            _enemies.Configure(Player,"normal",()=>Score,v=>Score=Mathf.Max(0,Score+v));
        }

        public void UpdateWorld(PlayerInputState input)
        {
            if(Dead)return; Player.Move(input.Move); if(input.Laser)Player.FireLaser(); if(input.Torpedo)Player.FireTorpedo();
            float bonus=_background.CurrentSystemBonus;var profile=GameConstants.Normal;float density=profile.AsteroidDensity*(1f+bonus*.8f);float interval=Mathf.Max(GameConstants.AsteroidMinSpawnIntervalFrames,GameConstants.AsteroidSpawnIntervalFrames/Mathf.Max(.35f,density));
            _spawnTimer++; if(_spawnTimer>=interval){SpawnAsteroid(profile.AsteroidSize*(1f+bonus*.18f),_background.AsteroidSpeedMultiplier*profile.AsteroidSpeed*(1f+bonus*.7f));_spawnTimer=0;}
            _background.UpdateBackground(Score);
            for(int i=_asteroids.Count-1;i>=0;i--)if(_asteroids[i]==null||!_asteroids[i].Alive)_asteroids.RemoveAt(i);
            for(int i=_projectiles.Count-1;i>=0;i--)if(_projectiles[i]==null||!_projectiles[i].Alive)_projectiles.RemoveAt(i);
            HandlePlayerAsteroids();
        }

        private void SpawnAsteroid(float size,float speed){var go=new GameObject("PointsAsteroid");var a=go.AddComponent<AsteroidController>();a.Initialize(_assets.Asteroids,size,speed);a.Destroyed+=(x)=>{Score+=x.Points;if(_assets.Explosion!=null)ExplosionController.Spawn(_assets.Explosion,x.transform.position,x.ScaleMultiplier);};_asteroids.Add(a);}
        private void HandlePlayerAsteroids(){if(Player==null||Player.IsInvulnerable)return;foreach(var a in _asteroids){if(a==null||!a.Alive)continue;if(a.PixelRect().Overlaps(new Rect(Player.PixelPosition.x,Player.PixelPosition.y,96,96))){a.DestroyAsteroid();Player.TakeDamage();break;}}}
    }

    public sealed class PointsFightSession : MonoBehaviour
    {
        public PointsFightWorld Player1World{get;private set;} public PointsFightWorld Player2World{get;private set;} public bool MatchOver{get;private set;}
        [SerializeField] private AssetLibrary assets;[SerializeField] private LocalInputRouter input;
        private float _elapsed;

        private void Start(){if(input==null)input=FindObjectOfType<LocalInputRouter>();if(assets==null)assets=FindObjectOfType<AssetLibrary>();var ships=RuntimeContent.BuildShips(assets);Player1World=new PointsFightWorld("Spieler 1",Faction.Rebels,ships[ShipId.XWing],assets);Player2World=new PointsFightWorld("Spieler 2",Faction.Empire,ships[ShipId.TieFighter],assets);}
        private void Update(){if(MatchOver||Player1World==null)return;_elapsed+=Time.deltaTime;if(_elapsed>=GameConstants.PvPScoreLimitMs/1000f||Player1World.Dead&&Player2World.Dead){MatchOver=true;return;}Player1World.UpdateWorld(input!=null?input.ReadPlayer1():default);Player2World.UpdateWorld(input!=null?input.ReadPlayer2():default);}
    }
}
