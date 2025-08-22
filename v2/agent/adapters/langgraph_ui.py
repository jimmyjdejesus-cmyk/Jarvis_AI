"""Workflow visualisation utilities for Jarvis V2.

This module provides a ``WorkflowVisualizer`` capable of consuming
workspace events and exporting the resulting graph in multiple formats
(``json``, ``dot`` or ``png``).  It is intentionally lightweight and makes
no assumptions about the upstream event source – events simply need an
``id`` and ``type`` and may optionally define edge relationships such as
``produces`` or ``consumes``.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Iterable, List

from graphviz import Digraph


# ---------------------------------------------------------------------------
# Data structures


@dataclass
class Node:
    """Representation of a workflow node."""

    id: str
    type: str
    label: str | None = None
    color: str | None = None
    badges: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """Representation of a workflow edge."""

    source: str
    target: str
    type: str


# ---------------------------------------------------------------------------
# Visualiser implementation


class WorkflowVisualizer:
    """Build and export workflow graphs."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

    # ------------------------------------------------------------------
    def add_event(self, event: Dict[str, Any]) -> None:
        """Ingest a single workflow event.

        Parameters
        ----------
        event:
            Dictionary describing the event.  Expected keys:

            ``id`` (str)
                Unique identifier for the node.
            ``type`` (str)
                Node type such as ``Team`` or ``ToolCall``.
            ``label`` (str, optional)
                Human friendly label for visualisations.
            ``color`` (str, optional)
                Optional colour for the node.
            ``scope``, ``status`` and ``score`` are stored as badge
            information.  Any other key-value pairs are preserved in the
            node's ``meta`` field.

            Edge relationships can be expressed using ``produces``,
            ``consumes``, ``merged_into`` and ``derived_from`` which should
            each contain an iterable of target node IDs.
        """

        node_id = str(event.get("id"))
        if not node_id:
            raise ValueError("event must contain an 'id'")

        node_type = event.get("type", "unknown")
        label = event.get("label", node_id)
        color = event.get("color")

        badges = {
            key: event.get(key)
            for key in ("scope", "status", "score")
            if key in event
        }

        known_fields = {
            "id",
            "type",
            "label",
            "color",
            "produces",
            "consumes",
            "merged_into",
            "derived_from",
            "scope",
            "status",
            "score",
        }

        meta = {k: v for k, v in event.items() if k not in known_fields}

        self.nodes[node_id] = Node(
            id=node_id,
            type=node_type,
            label=label,
            color=color,
            badges=badges,
            meta=meta,
        )

        for edge_type in ("produces", "consumes", "merged_into", "derived_from"):
            for target in event.get(edge_type, []) or []:
                self.edges.append(Edge(source=node_id, target=str(target), type=edge_type))

    # ------------------------------------------------------------------
    def add_events(self, events: Iterable[Dict[str, Any]]) -> None:
        """Bulk add multiple events."""

        for event in events:
            self.add_event(event)

    # ------------------------------------------------------------------
    def _build_graph(self) -> Digraph:
        graph = Digraph(comment="Workflow")

        for node in self.nodes.values():
            attrs = {}
            if node.color:
                attrs["color"] = node.color
                attrs["style"] = "filled"
            graph.node(node.id, node.label or node.id, **attrs)

        for edge in self.edges:
            graph.edge(edge.source, edge.target, label=edge.type)

        return graph

    # ------------------------------------------------------------------
    def export(self, fmt: str = "json") -> Any:
        """Export the graph in the requested format."""

        fmt = fmt.lower()
        if fmt == "json":
            return {
                "nodes": [asdict(node) for node in self.nodes.values()],
                "edges": [asdict(edge) for edge in self.edges],
            }

        graph = self._build_graph()

        if fmt == "dot":
            return graph.source
        if fmt == "png":
            # ``pipe`` returns ``bytes`` containing the rendered image
            return graph.pipe(format="png")

        raise ValueError(f"Unsupported format: {fmt}")


# Expose a module-level visualiser that can be reused by the API server
visualizer = WorkflowVisualizer()


def render_langgraph_ui(workflow: Any, events: Iterable[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Render a LangGraph UI component using the provided events."""

    visualizer = WorkflowVisualizer()
    if events:
        visualizer.add_events(events)
    return visualizer.export("json")


__all__ = ["WorkflowVisualizer", "visualizer", "render_langgraph_ui"]

