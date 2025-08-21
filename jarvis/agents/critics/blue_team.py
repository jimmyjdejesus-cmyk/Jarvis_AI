"""Blue Team critic for assessing strategic risk, ethics, and external impacts.

This critic reviews synthesized outputs to detect potential issues before
presenting them to users or downstream systems.

Expected output structure from :meth:`evaluate`::

    {
        "risk_score": float,              # 0.0 (no risk) to 1.0 (high risk)
        "ethical_flags": List[str],       # Detected ethical concerns
        "external_impacts": List[str],    # Potential external effects
        "requires_escalation": bool,      # True when risk >= sensitivity
        "escalation_path": str            # Recommended escalation target
    }

Escalation path values:
    - ``"none"``: No additional action required.
    - ``"notify_human"``: Alert human oversight for review.
    - ``"halt"``: Immediate stop of related processes recommended.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List


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

        if not payload.get("success", True):
            risk_score = 1.0
            external_impacts.append("Potential system instability detected")
        else:
            # Very naive heuristic: larger error messages imply higher risk.
            message = str(payload)
            if "error" in message.lower():
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
