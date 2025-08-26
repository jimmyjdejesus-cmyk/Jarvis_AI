from __future__ import annotations

"""Minimal root cause analyzer for failed trajectories."""

from collections import Counter
from typing import Any, Dict, List


class RootCauseAnalyzer:
    """Identify the most likely component causing a failure.

    The analyzer maintains a running count of component failures and combines
    this history with evidence from the provided trajectory.  Components that
    appear more frequently in the failing trajectory or have a higher failure
    history are considered more likely culprits.  This lightweight approach
    avoids heavy simulation while still providing actionable insight.
    """

    def __init__(self) -> None:
        self.failure_counts: Counter[str] = Counter()

    # ------------------------------------------------------------------
    def analyze(self, trajectory: List[str], dependencies: List[str]) -> Dict[str, Any]:
        """Return the most likely failing component.

        Parameters
        ----------
        trajectory: List[str]
            Sequence of steps leading to the failure.
        dependencies: List[str]
            Components involved in the failing strategy.

        Returns
        -------
        Dict[str, Any]
            Mapping containing the component and reasoning.
        """

        if not dependencies:
            return {"component": "unknown", "reason": "no dependencies provided"}

        scores: Dict[str, int] = {}
        for dep in dependencies:
            freq = sum(step.count(dep) for step in trajectory)
            scores[dep] = freq + self.failure_counts[dep]

        component = max(scores, key=scores.get)
        self.failure_counts[component] += 1
        return {"component": component, "reason": f"{component} correlated with failure"}


__all__ = ["RootCauseAnalyzer"]
