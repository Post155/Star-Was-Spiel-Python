"""Input handling used exclusively by the local two-player PvP mode.

The normal single-player and LAN modes never import or use this module.
Player 1 controls the lower ship with WASD/WS, player 2 controls the upper
ship with the arrow keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pygame

from game.constants import LOCAL_PVP_KEY_BINDINGS


@dataclass(frozen=True)
class LocalPvPPlayerInput:
    left: int
    right: int
    laser: int
    torpedo: int


class LocalPvPInput:
    """Collect simultaneous keyboard state for both local PvP players."""

    def __init__(self) -> None:
        self.bindings = {
            player_id: LocalPvPPlayerInput(
                left=getattr(pygame, binding["left"]),
                right=getattr(pygame, binding["right"]),
                laser=getattr(pygame, binding["laser"]),
                torpedo=getattr(pygame, binding["torpedo"]),
            )
            for player_id, binding in LOCAL_PVP_KEY_BINDINGS.items()
        }
        self._fire_events: List[tuple[str, str]] = []
        self.quit_requested = False

    def reset(self) -> None:
        self._fire_events.clear()
        self.quit_requested = False

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.quit_requested = True
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.quit_requested = True
            return

        for player_id, mapping in self.bindings.items():
            if event.key == mapping.laser:
                self._fire_events.append((player_id, "laser"))
            elif event.key == mapping.torpedo:
                self._fire_events.append((player_id, "torpedo"))

    def consume_fire_events(self) -> List[tuple[str, str]]:
        events = list(self._fire_events)
        self._fire_events.clear()
        return events

    def get_states(self) -> Dict[str, Dict[str, bool]]:
        keys = pygame.key.get_pressed()
        states: Dict[str, Dict[str, bool]] = {}
        for player_id, mapping in self.bindings.items():
            states[player_id] = {
                "left": bool(keys[mapping.left]),
                "right": bool(keys[mapping.right]),
            }
        return states

    @staticmethod
    def control_text() -> str:
        return (
            "P1: A/D bewegen • W Laser • S Torpedo    "
            "P2: ←/→ bewegen • ↑ Laser • ↓ Torpedo"
        )
