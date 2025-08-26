from __future__ import annotations

"""Lightweight rule-based predictive simulation model."""

from typing import Dict, List


class PredictiveSimulator:
    """Heuristic simulator estimating outcomes of simple actions.

    The simulator maintains a minimal numeric ``value`` within the
    provided state.  Actions containing certain keywords adjust this
    value, allowing agents to estimate how a sequence of actions might
    influence the environment.  Scores are normalized to the ``[0, 1]``
    range for easy comparison.
    """

    def predict(self, state: Dict[str, int], action: str) -> Dict[str, int]:
        """Return predicted next state after applying ``action``.

        Parameters
        ----------
        state:
            Current simulation state.  Missing ``value`` defaults to ``0``.
        action:
            Description of the proposed action.
        """
        value = state.get("value", 0)
        text = action.lower()
        if "increase" in text or "build" in text:
            value += 1
        elif "decrease" in text or "remove" in text:
            value -= 1
        return {"value": value}

    def evaluate(self, state: Dict[str, int], action: str) -> float:
        """Return a heuristic desirability score for ``action``.

        The higher the resulting ``value`` after prediction, the better
        the score.  Values are clamped to the ``[0, 1]`` range.
        """
        next_state = self.predict(state, action)
        value = next_state.get("value", 0)
        return max(0.0, min(1.0, 0.5 + value / 10.0))

    def rank_actions(self, state: Dict[str, int], actions: List[str]) -> List[str]:
        """Order ``actions`` from most to least promising."""
        return sorted(actions, key=lambda a: self.evaluate(state, a), reverse=True)


__all__ = ["PredictiveSimulator"]
