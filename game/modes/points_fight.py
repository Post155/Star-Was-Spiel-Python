"""Points-fight adapter for the modular structure."""

from game.StarWarsGame import run_local_pvp_flow


def run_points_fight_flow(*args, **kwargs):
    """Start the local points-fight flow through the existing runtime."""
    return run_local_pvp_flow("points")


__all__ = ["run_points_fight_flow"]
