"""Hierarchical project memory with provenance and hypergraph layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import networkx as nx

# Layer constants
L1_FACT = "fact"
L2_STRATEGY = "strategy"
L3_BELIEF = "belief"
L4_CONSTITUTION = "constitutional"


@dataclass(frozen=True)
class Namespace:
    """Namespace identifiers for project memory.

    Attributes
    ----------
    project:
        Project identifier.
    session:
        Session identifier.
    team:
        Team identifier.
    """

    project: str
    session: str
    team: str


class ProjectMemory:
    """Store and relate memories across project namespaces.

    Each namespace maintains a directed graph where nodes represent memory
    entries annotated with their layer and provenance (``run_id`` and
    ``mission_id``). Edges connect related entries, enabling a simple
    hypergraph structure.
    """

    def __init__(self) -> None:
        self._graphs: Dict[Tuple[str, str, str], nx.DiGraph] = {}

    def _key(self, ns: Namespace) -> Tuple[str, str, str]:
        return (ns.project, ns.session, ns.team)

    def add_entry(
        self,
        ns: Namespace,
        layer: str,
        content: str,
        run_id: str,
        mission_id: str,
        links: Optional[List[str]] = None,
    ) -> str:
        """Add a memory entry to ``ns`` and return its node identifier."""

        graph = self._graphs.setdefault(self._key(ns), nx.DiGraph())
        node_id = str(uuid4())
        graph.add_node(
            node_id,
            layer=layer,
            content=content,
            run_id=run_id,
            mission_id=mission_id,
        )
        if links:
            for target in links:
                if graph.has_node(target):
                    graph.add_edge(node_id, target)
        return node_id

    def get_graph(self, ns: Namespace) -> nx.DiGraph:
        """Return the graph for ``ns`` (creating if necessary)."""
        return self._graphs.setdefault(self._key(ns), nx.DiGraph())


__all__ = [
    "ProjectMemory",
    "Namespace",
    "L1_FACT",
    "L2_STRATEGY",
    "L3_BELIEF",
    "L4_CONSTITUTION",
]
