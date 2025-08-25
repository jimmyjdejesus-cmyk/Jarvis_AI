from __future__ import annotations

"""Lightweight branch simulation hooks for scout and scholar roles."""

from typing import Any, Dict, Tuple

from jarvis.world_model.hypergraph import HierarchicalHypergraph
from .root_cause_analyzer import RootCauseAnalyzer


def simulate(
    branch_spec: Dict[str, Any],
    hypergraph: HierarchicalHypergraph,
    analyzer: RootCauseAnalyzer | None = None,
) -> Tuple[float, str, Dict[str, Any]]:
    """Simulate a branch and return its score, notes and diffs.

    Parameters
    ----------
    branch_spec:
        Description of the branch. The ``type`` field selects between ``scout``
        and ``scholar`` modes. ``scout`` expects ``strategy_id`` while
        ``scholar`` expects ``neg_path_id`` and an optional ``budget``.
    hypergraph:
        Knowledge graph used for retrieving strategy information.
    analyzer:
        Optional root cause analyzer used for scholar branches when an explicit
        root cause is not already recorded.
    """

    branch_type = branch_spec.get("type")
    notes = ""
    diffs: Dict[str, Any] = {}

    if branch_type == "scout":
        strategy_id = branch_spec["strategy_id"]
        node = hypergraph.query(2, strategy_id) or {}
        score = float(node.get("confidence", 0.5))
        notes = f"scouted {strategy_id}"
        diffs = {"candidate": strategy_id}
        return score, notes, diffs

    if branch_type == "scholar":
        neg_id = branch_spec["neg_path_id"]
        budget = min(branch_spec.get("budget", 0.1), 0.1)
        neg_node = hypergraph.query(2, neg_id) or {}
        rca = neg_node.get("root_cause")
        if not rca:
            analyzer = analyzer or RootCauseAnalyzer()
            strategy_key = neg_node.get("strategy")
            strategy_node = hypergraph.query(2, strategy_key) or {}
            trajectory = strategy_node.get("steps", [])
            dependencies = strategy_node.get("dependencies", [])
            rca = analyzer.analyze(trajectory, dependencies)
        notes = f"RCA for {neg_id}"
        diffs = {"rca": rca, "budget": budget}
        return 0.0, notes, diffs

    raise ValueError(f"unknown branch type: {branch_type}")


__all__ = ["simulate"]
