from __future__ import annotations

"""Shared critic API for multi-stage review pipeline."""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class CriticVerdict:
    """Standard verdict returned by critics.

    Attributes
    ----------
    approved:
        Whether the artifact passed the critic's review.
    fixes:
        Suggested fixes to address identified issues.
    risk:
        Numeric risk score in ``[0,1]`` where higher values indicate
        greater external impact.
    notes:
        Additional notes or rationale from the critic.
    """

    approved: bool
    fixes: List[str]
    risk: float
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable dictionary representation."""
        return asdict(self)
