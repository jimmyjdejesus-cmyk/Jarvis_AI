from __future__ import annotations

"""Simple REX-RAG policy optimizer with failure analysis."""

from typing import Dict, Any

from jarvis.world_model.hypergraph import HierarchicalHypergraph
from .root_cause_analyzer import RootCauseAnalyzer
from .remediation_agent import RemediationAgent


class PolicyOptimizer:
    """Update strategy confidence based on reward feedback."""

    def __init__(
        self,
        hypergraph: HierarchicalHypergraph,
        learning_rate: float = 0.1,
        root_cause_analyzer: RootCauseAnalyzer | None = None,
        remediation_agent: RemediationAgent | None = None,
    ) -> None:
        self.hypergraph = hypergraph
        self.learning_rate = learning_rate
        self.history: list[Dict[str, Any]] = []
        self.root_cause_analyzer = root_cause_analyzer or RootCauseAnalyzer()
        self.remediation_agent = remediation_agent or RemediationAgent()

    def update_strategy(self, strategy_key: str, reward: float) -> None:
        """Adjust the confidence of a strategy node using REX-RAG update rule."""
        node = self.hypergraph.query(2, strategy_key)
        if not node:
            return
        confidence = node.get("confidence", 0.5)
        updated = confidence + self.learning_rate * (reward - confidence)
        self.hypergraph.update_node(2, strategy_key, {"confidence": updated})
        self.history.append({"strategy": strategy_key, "reward": reward, "confidence": updated})

        if reward == 0.0:
            trajectory = node.get("steps", [])
            dependencies = node.get("dependencies", [])
            root_cause = self.root_cause_analyzer.analyze(trajectory, dependencies)
            self.hypergraph.add_negative_pathway(strategy_key, root_cause)
            self.remediation_agent.remediate(root_cause["component"])
