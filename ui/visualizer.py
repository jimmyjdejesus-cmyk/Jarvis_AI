"""Workflow visualisation utilities.

The ``WorkflowVisualizer`` consumes a list of event dictionaries – typically the
same structures emitted by the streaming endpoint – and produces Graphviz DOT
files or PNG renderings.  It is intentionally flexible; events only need to
specify a ``step`` name and optionally a list of ``depends`` describing edges in
the workflow graph.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, Any

from graphviz import Digraph


class WorkflowVisualizer:
    """Create visual representations of workflow execution."""

    def __init__(self, events: Iterable[Dict[str, Any]]):
        self.events = list(events)

    # ------------------------------------------------------------------
    def _build_graph(self) -> Digraph:
        graph = Digraph(comment="Workflow")

        for event in self.events:
            step = str(event.get("step") or event.get("step_id"))
            if not step:
                continue

            status = event.get("status", "active")
            color = "red" if status == "pruned" else "green"
            graph.node(step, step, color=color, style="filled")

            parent = event.get("parent_id")
            if parent:
                graph.edge(str(parent), step)
            for dep in event.get("depends", []):
                graph.edge(str(dep), step)
            for src in event.get("merged_from", []):
                graph.edge(str(src), step, style="dashed")
        return graph

    # ------------------------------------------------------------------
    def export_dot(self, path: str | Path) -> str:
        """Write the workflow to a DOT file and return the path."""

        graph = self._build_graph()
        path = str(path)
        graph.save(path)
        return path

    # ------------------------------------------------------------------
    def export_png(self, path: str | Path) -> str:
        """Render the workflow to a PNG image and return the file path."""

        graph = self._build_graph()
        path = str(path)
        output_path = graph.render(path, format="png", cleanup=True)
        return output_path


__all__ = ["WorkflowVisualizer"]

