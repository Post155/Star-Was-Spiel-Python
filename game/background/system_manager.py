"""SystemManager: manage star system order, selection and difficulty.

Responsibility:
- Build systems from configuration
- Provide current system and ordering operations
- Encapsulate visited tracking and next-system selection
"""
from typing import List, Optional, Set
import random
from .systems import StarSystem, build_systems


class SystemManager:
    def __init__(self, assets: Optional[dict] = None) -> None:
        self.assets = assets or {}
        self.systems: List[StarSystem] = build_systems(self.assets)

        if self.systems:
            first = self.systems[0]
            others = self.systems[1:]
            random.shuffle(others)
            self.order: List[StarSystem] = [first] + others
        else:
            self.order = []

        self.order_index: int = 0
        self.level_index: int = 0
        self.visited: Set[str] = set()

    def current_system(self) -> Optional[StarSystem]:
        if not self.order:
            return None
        return self.order[self.order_index]

    def current_level_name(self) -> str:
        sys = self.current_system()
        return sys.id_name if sys else ''

    def current_level_index(self) -> int:
        return self.level_index

    def next_index(self) -> int:
        if not self.order:
            return 0
        return (self.order_index + 1) % len(self.order)

    def target_system(self) -> Optional[StarSystem]:
        if not self.order:
            return None
        return self.order[self.next_index()]

    def advance_to_index(self, idx: int) -> None:
        if not self.order:
            return
        self.order_index = idx % len(self.order)
        self.level_index = 0

    def mark_visited_current(self) -> None:
        sys = self.current_system()
        if sys:
            self.visited.add(sys.id_name)

    def get_all_systems(self) -> List[StarSystem]:
        return list(self.order)

    def get_current_difficulty(self) -> int:
        sys = self.current_system()
        return getattr(sys, 'difficulty', 1) if sys else 1

    def get_current_system_id(self) -> str:
        sys = self.current_system()
        return getattr(sys, 'id_name', '') if sys else ''

    def get_available_planet_keys(self, system: Optional[StarSystem], assets: dict) -> List[str]:
        if system is None:
            return []
        keys = []
        for k in getattr(system, 'planet_keys', []) or []:
            candidates = [f"{k}_img", k]
            found = False
            for c in candidates:
                if c in assets and assets.get(c) is not None:
                    keys.append(k)
                    found = True
                    break
            if not found:
                k2 = k.replace('_planet', '').replace('planet_', '')
                for c in (f"{k2}_img", k2):
                    if c in assets and assets.get(c) is not None:
                        keys.append(k)
                        break
        return keys
