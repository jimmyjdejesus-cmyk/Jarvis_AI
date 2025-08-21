"""Critic agents for evaluating specialist outputs for quality control."""

from .red_team import RedTeamCritic
from .blue_team import BlueTeamCritic

__all__ = ["RedTeamCritic", "BlueTeamCritic"]
