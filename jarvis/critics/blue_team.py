"""Blue team critic for assessing strategic risk and ethical impact.

The blue team critic evaluates final outputs to detect potential risks or
ethical concerns before presenting results to users or downstream systems.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class BlueTeamCritic:
    """Evaluate final outputs for risks and ethical considerations.

    Parameters
    ----------
    sensitivity: float, optional
        Threshold above which escalation is triggered. Defaults to ``0.5``.
    """

    sensitivity: float = 0.5

    def evaluate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Assess a payload for risk and ethics.

        Parameters
        ----------
        payload: Dict[str, Any]
            The synthesized result to critique.

        Returns
        -------
        Dict[str, Any]
            Structured critique including risk scores and escalation guidance.
        """
        risk_score = 0.0
        ethical_flags: List[str] = []
        external_impacts: List[str] = []

        if not payload.get("success", False):
            risk_score = 1.0
            external_impacts.append("Potential system instability detected")
        else:
            message = str(payload)
            error_value = payload.get("error")
            if error_value or "error" in message.lower():
                risk_score = 0.7
                ethical_flags.append("Unhandled error present")

        requires_escalation = risk_score >= self.sensitivity
        escalation_path = "notify_human" if requires_escalation else "none"

        return {
            "risk_score": risk_score,
            "ethical_flags": ethical_flags,
            "external_impacts": external_impacts,
            "requires_escalation": requires_escalation,
            "escalation_path": escalation_path,
        }
