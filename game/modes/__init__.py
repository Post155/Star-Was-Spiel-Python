"""Game-mode adapters for the current project structure."""

from .last_survivor import run_last_survivor_flow
from .local_pvp import run_local_pvp_flow
from .points_fight import run_points_fight_flow
from .pvp_duel import run_pvp_flow
from .singleplayer import run_singleplayer_flow

__all__ = [
    "run_singleplayer_flow",
    "run_local_pvp_flow",
    "run_pvp_flow",
    "run_points_fight_flow",
    "run_last_survivor_flow",
]
