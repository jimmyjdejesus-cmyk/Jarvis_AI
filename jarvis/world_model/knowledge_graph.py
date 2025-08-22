"""Graph-based world model for code understanding."""

from __future__ import annotations

from typing import Any, Dict, Optional

import networkx as nx


class KnowledgeGraph:
    """Central repository of code entities and their relationships."""

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

    # ------------------------------------------------------------------
    def add_node(
        self, node_id: str, node_type: str, attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a node with a type and optional attributes."""

        attrs = {"type": node_type}
        if attributes:
            attrs.update(attributes)
        self.graph.add_node(node_id, **attrs)

    # ------------------------------------------------------------------
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a typed edge between two nodes."""

        attrs = {"type": relationship_type}
        if attributes:
            attrs.update(attributes)
        self.graph.add_edge(source_id, target_id, **attrs)

    # ------------------------------------------------------------------
    def query(self, query: str) -> Any:
        """Execute a very small subset of Cypher-like queries.
        The supported forms are:
        - ``"nodes"`` – return all nodes with data
        - ``"edges"`` – return all edges with data
        - ``"node <id>"`` – return data for a specific node
        """

        if query == "nodes":
            return list(self.graph.nodes(data=True))
        if query == "edges":
            return list(self.graph.edges(data=True))
        if query.startswith("node "):
            node_id = query.split(" ", 1)[1]
            return self.graph.nodes.get(node_id)
        raise ValueError("Unsupported query")

    # ------------------------------------------------------------------
    def get_files(self) -> list[str]:
        """Return identifiers of all file nodes."""

        return [n for n, data in self.graph.nodes(data=True) if data.get("type") == "file"]