"""World model components for persistent repository understanding."""
from __future__ import annotations

# KnowledgeGraph requires heavy optional dependencies (e.g. ``networkx``). The
# import is guarded so tests can run in minimal environments.
try:  # pragma: no cover - optional dependency
    from .knowledge_graph import KnowledgeGraph  # type: ignore
except Exception:  # pragma: no cover
    KnowledgeGraph = None  # type: ignore

from .hypergraph import HierarchicalHypergraph
from .predictive_simulation import PredictiveSimulator
from .neo4j_graph import Neo4jGraph

__all__ = [
    "KnowledgeGraph",
    "HierarchicalHypergraph",
    "PredictiveSimulator",
    "Neo4jGraph",
]