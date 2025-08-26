"""Agent that generates self-directed research questions from low confidence knowledge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jarvis.world_model.hypergraph import HierarchicalHypergraph


@dataclass
class CuriosityAgent:
    """Scans the hypergraph for uncertain knowledge and proposes research questions."""

    hypergraph: HierarchicalHypergraph
    threshold: float = 0.5

    def generate_question(self) -> Optional[str]:
        """Return a research question about low-confidence knowledge.

        Scans all layers for nodes or relationships whose confidence is below the
        configured threshold. If one is found, a natural language question is
        produced asking for clarification or evidence.
        """

        low_conf = self.hypergraph.get_low_confidence_nodes(self.threshold)
        if not low_conf:
            return None
        layer, key, data = low_conf[0]
        description = data.get("description") or key.replace("_", " ")
        return f"What evidence can improve our understanding of {description}?"


__all__ = ["CuriosityAgent"]
