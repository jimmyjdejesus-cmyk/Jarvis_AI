"""Critic components for reviewing agent outputs."""
from .red_team import RedTeamCritic
from .blue_team import BlueTeamCritic

__all__ = ["RedTeamCritic", "BlueTeamCritic"]
