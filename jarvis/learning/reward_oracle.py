from __future__ import annotations

"""Lightweight reward oracle for scoring branch simulations."""

from typing import Any, Mapping


class RewardOracle:
    """Compute reward for a branch including penalty for resource use."""

    def __init__(self, penalty_weight: float = 1.0) -> None:
        """Create oracle with configurable penalty weight."""
        self.penalty_weight = penalty_weight

    # ------------------------------------------------------------------
    def score(self, base_score: float, diffs: Mapping[str, Any]) -> float:
        """Return reward adjusted by penalties in ``diffs``.

        Parameters
        ----------
        base_score:
            Raw score from the simulation.
        diffs:
            Dictionary of branch metadata. The ``budget`` field, when present,
            is treated as a non-negative penalty.
        """

        penalty = max(0.0, float(diffs.get("budget", 0.0)))
        return float(base_score) - self.penalty_weight * penalty


__all__ = ["RewardOracle"]