"""Pruning evaluator and simple merge utilities.

This module implements the ``PruningEvaluator`` service described in the
specification.  It provides in‑process scoring of exploration teams and emits
pruning recommendations via the shared :class:`MessageBus`.

The implementation intentionally keeps the scoring heuristics lightweight so it
can operate without external ML dependencies.  It nevertheless exposes the
required interfaces making it easy to swap in a more sophisticated evaluator in
the future.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from .message_bus import MessageBus


@dataclass
class Scores:
    """Container for pruning score signals."""

    novelty: float
    growth: float
    cost: float


class PruningEvaluator:
    """Score teams and emit prune suggestions.

    Parameters
    ----------
    bus:
        Message bus used for publishing events.
    scope:
        Optional scope identifier for event publication.
    config:
        Threshold configuration.  Supports ``min_novelty``, ``min_growth`` and
        ``max_cost_per_gain``.
    """

    def __init__(
        self,
        bus: MessageBus,
        scope: str = "global",
        config: Optional[Dict[str, float]] = None,
    ) -> None:
        self.bus = bus
        self.scope = scope
        self.config = {
            "min_novelty": 0.25,
            "min_growth": 0.0,
            "max_cost_per_gain": 3.0,
        }
        if config:
            self.config.update(config)

        # Store simple per‑team history for delta calculations
        self._history: Dict[str, List[Dict[str, Any]]] = {}

    async def score(self, team_id: str, output: Dict[str, Any]) -> Scores:
        """Calculate pruning scores for a team's latest output.

        The current implementation uses naive heuristics:

        * **Novelty** – lexical difference from the previous output
        * **Growth** – improvement in ``quality`` field
        * **Cost** – ``cost`` divided by quality gain (lower is better)
        """

        history = self._history.setdefault(team_id, [])

        # Novelty: simple token overlap with last output
        novelty = 1.0
        if history:
            prev_text = history[-1].get("text", "")
            cur_text = output.get("text", "")
            prev_tokens = set(prev_text.split())
            cur_tokens = set(cur_text.split())
            union = prev_tokens | cur_tokens
            if union:
                novelty = 1 - (len(prev_tokens & cur_tokens) / len(union))

        # Growth: difference in quality metric
        prev_quality = history[-1].get("quality", 0.0) if history else 0.0
        quality = output.get("quality", 0.0)
        growth = quality - prev_quality

        # Cost per gain: avoid division by zero
        cost = output.get("cost", 0.0)
        cost_per_gain = cost / growth if growth else float("inf")

        history.append(output)
        return Scores(novelty=novelty, growth=growth, cost=cost_per_gain)

    async def evaluate(self, team_id: str, output: Dict[str, Any]) -> Scores:
        """Score and publish prune suggestions when thresholds are violated."""

        scores = await self.score(team_id, output)
        cfg = self.config
        if (
            scores.novelty < cfg["min_novelty"]
            or scores.growth < cfg["min_growth"]
            or scores.cost > cfg["max_cost_per_gain"]
        ):
            await self.bus.publish(
                "orchestrator.prune_suggested",
                {
                    "team_id": team_id,
                    "scores": scores.__dict__,
                    "reason": "thresholds_not_met",
                },
                scope=self.scope,
            )
        return scores

    async def merge_state(
        self, from_team: str, into_team: str, artifacts: List[str]
    ) -> None:
        """Emit merge event consolidating team artifacts."""

        await self.bus.publish(
            "orchestrator.team_merged",
            {
                "from_team": from_team,
                "into_team": into_team,
                "merged_artifacts": artifacts,
            },
            scope=self.scope,
        )

    async def mark_dead_end(self, team_id: str, signature: str) -> None:
        """Publish dead‑end marker for a team path."""

        await self.bus.publish(
            "orchestrator.path_dead_end",
            {"team_id": team_id, "path_signature": signature},
            scope=self.scope,
        )
