"""Blue team critic for assessing strategic risk and ethical impact."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .api import CriticVerdict


@dataclass
class BlueTeamCritic:
    """Evaluate final outputs for risks and ethical considerations."""

    sensitivity: float = 0.5

    def review(self, artifact: Dict[str, Any], trace: Dict[str, Any] | None = None) -> CriticVerdict:
        """Assess a payload and return :class:`CriticVerdict`."""
        risk_score = 0.0
        fixes: List[str] = []

        if not artifact.get("success", False):
            risk_score = 1.0
        else:
            message = str(artifact)
            error_value = artifact.get("error")
            if error_value or "error" in message.lower():
                risk_score = 0.7
                fixes.append("Handle error condition")

        notes = "HITL recommended" if risk_score >= self.sensitivity else ""
        return CriticVerdict(
            approved=risk_score < self.sensitivity,
            fixes=fixes,
            risk=risk_score,
            notes=notes,
        )
