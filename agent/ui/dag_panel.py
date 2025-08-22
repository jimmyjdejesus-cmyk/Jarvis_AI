"""Workflow visualizer for Streamlit DAG panel."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional
import json

try:
    from graphviz import Digraph
except Exception:  # pragma: no cover - graphviz optional
    Digraph = None  # type: ignore


@dataclass
class StepEvent:
    """Compact event emitted by the orchestrator."""

    run_id: str
    step_id: str
    parent_id: Optional[str]
    event_type: str
    payload: dict


class WorkflowVisualizer:
    """Builds a directed acyclic graph from step events.

    The graph can be rendered inside Streamlit or exported to multiple
    formats for replay and debugging.
    """

    def __init__(self) -> None:
        self.events: List[StepEvent] = []

    # ------------------------------------------------------------------
    # Event collection
    # ------------------------------------------------------------------
    def add_event(self, event: StepEvent) -> None:
        """Record a step event."""

        self.events.append(event)

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------
    def _build_graph(self) -> Digraph:
        if Digraph is None:  # pragma: no cover - graphviz optional
            raise RuntimeError("graphviz is not installed")
        dot = Digraph(comment="workflow")
        for event in self.events:
            label = f"{event.event_type}\n{event.step_id}"
            dot.node(event.step_id, label=label)
            if event.parent_id:
                dot.edge(event.parent_id, event.step_id)
        return dot

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    def export_dot(self, path: str) -> None:
        dot = self._build_graph()
        dot.save(path)

    def export_png(self, path: str) -> None:
        dot = self._build_graph()
        dot.format = "png"
        dot.render(path, cleanup=True)

    def export_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([asdict(e) for e in self.events], fh, indent=2)

    # ------------------------------------------------------------------
    # Streamlit integration
    # ------------------------------------------------------------------
    def streamlit_panel(self) -> None:  # pragma: no cover - UI rendering
        """Render the DAG in a Streamlit app with export buttons."""

        import streamlit as st

        dot = self._build_graph()
        st.graphviz_chart(dot.source, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Export DOT"):
                self.export_dot("workflow.dot")
                st.success("Exported workflow.dot")
        with col2:
            if st.button("Export JSON"):
                self.export_json("workflow.json")
                st.success("Exported workflow.json")
        with col3:
            if st.button("Export PNG"):
                self.export_png("workflow")
                st.success("Exported workflow.png")
