"""
state_machine.py
Lightweight state machine skeleton for Enemy AI states.
Includes enumerated states requested in the design.
"""
from enum import Enum, auto
from typing import Optional


class AIState(Enum):
    PATROL = auto()
    SEARCH = auto()
    ATTACK = auto()
    EVADE = auto()
    RETREAT = auto()
    FLANK = auto()
    GUARD_LEADER = auto()


class State:
    def __init__(self, ai_controller):
        self.ai = ai_controller

    def enter(self, prev_state: Optional['State']):
        pass

    def exit(self):
        pass

    def update(self, dt: float):
        pass


class StateMachine:
    def __init__(self, ai_controller):
        self.ai = ai_controller
        self.current_state: Optional[State] = None
        self.current_enum: Optional[AIState] = None

    def change_state(self, new_state_enum: AIState):
        if self.current_state is not None:
            try:
                self.current_state.exit()
            except Exception:
                pass
        self.current_enum = new_state_enum
        # create a default State object wrapper; users can subclass and set ai.state_machine.current_state
        self.current_state = State(self.ai)
        try:
            self.current_state.enter(None)
        except Exception:
            pass

    def update(self, dt: float):
        if self.current_state is not None:
            try:
                self.current_state.update(dt)
            except Exception:
                pass
