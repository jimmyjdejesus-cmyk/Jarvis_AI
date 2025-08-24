"""Graph-based retrieval utilities.

Provides helpers to construct and persist graphs used for
retrieval-augmented generation (RAG). The graphs are represented
using :mod:`networkx` directed graphs and stored in JSON node-link
format for portability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Tuple, Any

import networkx as nx


def build_graph(
    relationships: Iterable[Tuple[str, str, str]],
    node_attrs: Dict[str, Dict[str, Any]] | None = None,
) -> nx.DiGraph:
    """Build a directed graph from typed relationships.

    Args:
        relationships: Iterable of ``(source, target, relation_type)`` tuples.
        node_attrs: Optional mapping of node identifier to attribute dicts.

    Returns:
        A :class:`networkx.DiGraph` populated with the provided nodes and edges.
    """

    graph = nx.DiGraph()
    if node_attrs:
        for node_id, attrs in node_attrs.items():
            graph.add_node(node_id, **attrs)
    for source, target, rel in relationships:
        graph.add_edge(source, target, type=rel)
    return graph


def save_graph(graph: nx.DiGraph, path: Path) -> None:
    """Persist ``graph`` to ``path`` in JSON node-link format."""

    path.parent.mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(graph)
    path.write_text(json.dumps(data, indent=2))


def load_graph(path: Path) -> nx.DiGraph:
    """Load a graph previously saved with :func:`save_graph`."""

    data = json.loads(path.read_text())
    return nx.node_link_graph(data)


__all__ = ["build_graph", "save_graph", "load_graph"]
