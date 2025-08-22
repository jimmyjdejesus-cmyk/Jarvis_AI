"""Pruning evaluator to score teams for novelty, growth and cost."""
from __future__ import annotations

from typing import Callable, Dict, List, Sequence


def cosine_sim(a: Sequence[float], b: Sequence[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class PruningEvaluator:
    """Score team branches to determine whether they should be pruned."""

    def __init__(self, embed_fn: Callable[[str], Sequence[float]], cfg: Dict[str, float]):
        self.embed = embed_fn
        self.cfg = cfg

    def score(
        self,
        team_outputs: List[str],
        other_outputs: List[str],
        growth_series: List[float],
        cost_ms: int,
    ) -> Dict[str, float]:
        """Return novelty, growth and cost efficiency metrics."""
        window = int(self.cfg.get("window", len(team_outputs)))
        team_slice = team_outputs[-window:]
        v = self.embed("\n".join(team_slice))

        other_slice = other_outputs[-window:]
        others = [self.embed(x) for x in other_slice] or [v]
        centroid = [sum(vals) / len(vals) for vals in zip(*others)]

        novelty = max(0.0, 1.0 - cosine_sim(v, centroid))
        growth = (growth_series[-1] - growth_series[0]) if len(growth_series) > 1 else 0.0
        cost_per_gain = (cost_ms / 1000.0) / max(1e-6, growth + 1e-6)
        return {"novelty": novelty, "growth": growth, "cost_gain": cost_per_gain}
