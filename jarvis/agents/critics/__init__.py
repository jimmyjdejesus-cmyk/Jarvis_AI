"""Critic agents for evaluating specialist outputs for quality control."""
from dataclasses import dataclass
from typing import Any, Dict

from .blue_team import BlueTeamCritic
from .constitutional_critic import ConstitutionalCritic
from .red_team import RedTeamCritic
from jarvis.critics import CriticVerdict, WhiteGate


@dataclass
class CriticFeedback:
    """A simple dataclass to hold feedback from a critic."""
    critic_id: str
    message: str
    severity: str
    details: Dict[str, Any] = None


__all__ = [
    "RedTeamCritic",
    "BlueTeamCritic",
    "ConstitutionalCritic",
    "CriticVerdict",
    "WhiteGate",
    "CriticFeedback",
]
