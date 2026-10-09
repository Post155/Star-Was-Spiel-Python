using System.Collections.Generic;
using UnityEngine;

namespace StarWarsUnity
{
    public sealed class StarSystemManager : MonoBehaviour
    {
        public IReadOnlyList<StarSystemDefinition> Order => _order;
        public StarSystemDefinition Current => _order.Count == 0 ? null : _order[_index];
        public int CurrentIndex => _index;
        private readonly List<StarSystemDefinition> _systems = new List<StarSystemDefinition>();
        private readonly List<StarSystemDefinition> _order = new List<StarSystemDefinition>();
        private int _index;

        public void Initialize(AssetLibrary assets)
        {
            _systems.Clear(); _order.Clear(); _systems.AddRange(RuntimeContent.BuildSystems(assets));
            if (_systems.Count == 0) return;
            _order.Add(_systems[0]); _systems.RemoveAt(0);
            for (int i=_systems.Count-1;i>0;i--) { int j=Random.Range(0,i+1); (_systems[i],_systems[j])=(_systems[j],_systems[i]); }
            _order.AddRange(_systems); _index=0;
        }

        public int NextIndex() => _order.Count==0?0:(_index+1)%_order.Count;
        public StarSystemDefinition Target => _order.Count==0?null:_order[NextIndex()];
        public void AdvanceToIndex(int index){if(_order.Count==0)return;_index=((index%_order.Count)+_order.Count)%_order.Count;}
    }
}
