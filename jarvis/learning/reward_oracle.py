from __future__ import annotations

"""Lightweight reward oracle for scoring branch simulations."""

from typing import Dict


class RewardOracle:
    """Compute reward for a branch including penalty for resource use."""

    def __init__(self, penalty_weight: float = 1.0) -> None:
        self.penalty_weight = penalty_weight

    # ------------------------------------------------------------------
    def score(self, base_score: float, diffs: Dict[str, float]) -> float:
        """Return reward adjusted by penalties in ``diffs``.

        Parameters
        ----------
        base_score:
            Raw score from the simulation.
        diffs:
            Dictionary of branch metadata. The ``budget`` field, when present,
            is treated as a penalty.
        """

        penalty = float(diffs.get("budget", 0.0))
        return base_score - self.penalty_weight * penalty


__all__ = ["RewardOracle"]
