"""
boss.py
Simple BossPhase and BossEnemy helper. BossEnemy is intended to be used by EnemyManager to create special behavior.
"""
from typing import Callable, List, Optional

class BossPhase:
    def __init__(self, name: str, threshold_hp: Optional[float] = None, on_enter: Optional[Callable] = None):
        # threshold_hp is a fraction of max HP (e.g., 0.75, 0.5)
        self.name = name
        self.threshold_hp = threshold_hp
        self.on_enter = on_enter

class BossMixin:
    def __init__(self, phases: Optional[List[BossPhase]] = None):
        self.phases = phases or []
        self.current_phase_index = 0

    def check_phase_transition(self):
        if not hasattr(self, 'hp') or not hasattr(self, 'max_hp'):
            return
        hp_frac = float(self.hp) / max(1.0, float(self.max_hp))
        for i, p in enumerate(self.phases):
            if p.threshold_hp is not None and hp_frac <= p.threshold_hp and i != self.current_phase_index:
                self.current_phase_index = i
                if p.on_enter:
                    try:
                        p.on_enter(self)
                    except Exception:
                        pass

    def current_phase(self):
        if not self.phases:
            return None
        return self.phases[self.current_phase_index]
