"""Workflow visualizer for Streamlit DAG panel."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json
import time

from jarvis.observability.tracing import trace

try:
    from graphviz import Digraph
except Exception:  # pragma: no cover - graphviz optional
    Digraph = None  # type: ignore


@dataclass
class StepEvent:
    """Compact event emitted by the orchestrator.

    Additional metadata capture tool invocations, agent contributions and
    pruning/merge state so the visualiser can expose full reasoning paths.
    """

    run_id: str
    step_id: str
    parent_id: Optional[str]
    event_type: str
    payload: dict
    tool: Optional[str] = None
    agent: Optional[str] = None
    status: str = "active"
    merged_from: Optional[List[str]] = None
    reasoning: Optional[str] = None
    timestamp: float = field(default_factory=lambda: time.time())


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
        """Record a step event and emit a LangSmith trace."""

        self.events.append(event)
        try:
            with trace(
                "workflow_step",
                metadata={
                    "run_id": event.run_id,
                    "step_id": event.step_id,
                    "tool": event.tool,
                    "agent": event.agent,
                    "status": event.status,
                    "timestamp": event.timestamp,
                },
            ):
                pass
        except Exception:
            # LangSmith is optional; failures should not block visualization
            pass

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------
    def _build_graph(self) -> Digraph:
        if Digraph is None:  # pragma: no cover - graphviz optional
            raise RuntimeError("graphviz is not installed")
        dot = Digraph(comment="workflow")
        for event in self.events:
            label_lines = [event.event_type, event.step_id]
            if event.tool:
                label_lines.append(f"🔧 {event.tool}")
            if event.agent:
                label_lines.append(f"👤 {event.agent}")
            label = "\n".join(label_lines)
            color = {
                "pruned": "red",
                "merged": "blue",
            }.get(event.status, "green")
            dot.node(event.step_id, label=label, color=color, style="filled")
            if event.parent_id:
                dot.edge(event.parent_id, event.step_id)
            if event.merged_from:
                for src in event.merged_from:
                    dot.edge(src, event.step_id, style="dashed")
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
    # Event log rendering
    # ------------------------------------------------------------------
    def render_event_log(self, show_reasoning: bool = False) -> List[str]:
        """Return a formatted log of events.

        When ``show_reasoning`` is ``True`` the rationale for each event is
        included, allowing users to audit branches that were pruned or merged.
        """

        lines: List[str] = []
        for e in self.events:
            base = f"{e.timestamp:.0f} | {e.event_type}"
            if e.agent:
                base += f" | agent={e.agent}"
            if e.tool:
                base += f" | tool={e.tool}"
            if e.status != "active":
                base += f" | status={e.status}"
            if show_reasoning and e.reasoning:
                base += f" | reason={e.reasoning}"
            lines.append(base)
        return lines

    # ------------------------------------------------------------------
    # Streamlit integration
    # ------------------------------------------------------------------
    def streamlit_panel(self) -> None:  # pragma: no cover - UI rendering
        """Render the DAG in a Streamlit app with export buttons."""

        import streamlit as st

        dot = self._build_graph()
        st.graphviz_chart(dot.source, use_container_width=True)

        show_reasoning = st.checkbox("Show reasoning")
        for line in self.render_event_log(show_reasoning=show_reasoning):
            st.write(line)

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
