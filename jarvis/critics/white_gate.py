from __future__ import annotations

"""Quality gate that merges red and blue critic verdicts."""

from dataclasses import dataclass
from .api import CriticVerdict


@dataclass
class WhiteGate:
    """Aggregate critic verdicts and enforce policy thresholds."""

    risk_threshold: float = 0.5

    def merge(self, red: CriticVerdict, blue: CriticVerdict) -> CriticVerdict:
        """Merge red/blue verdicts into a final decision."""
        approved = red.approved and blue.risk < self.risk_threshold
        fixes = list(red.fixes)
        risk = max(blue.risk, 1.0 if not red.approved else blue.risk)
        notes_parts = []
        if not red.approved:
            notes_parts.append("red revision required")
        if blue.risk >= self.risk_threshold:
            notes_parts.append("HITL required")
        notes = "; ".join(notes_parts)
        return CriticVerdict(approved=approved, fixes=fixes, risk=risk, notes=notes)
