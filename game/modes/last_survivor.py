"""Last-survivor adapter."""

from game.local_pvp import LocalPvPDuelSession
from game.StarWarsGame import run_local_pvp_flow


def run_last_survivor_flow(*args, **kwargs):
    """Launch the local last-survivor mode using the existing duel flow."""
    return run_local_pvp_flow("last_survivor")


__all__ = ["LocalPvPDuelSession", "run_last_survivor_flow"]
