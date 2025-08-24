"""Real-time visualization and performance dashboard for Jarvis (Cerebro).

This module combines features from ``v2.agent.adapters.langgraph_ui`` and
``ui.visualizer`` to provide a lightweight web API that exposes a workflow
visualization. Events are expected to follow the
structure defined in ``schemas/event.json`` where the ``data`` field contains
node information understood by :class:`WorkflowVisualizer`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from v2.agent.adapters.langgraph_ui import WorkflowVisualizer


class CerebroDashboard:
    """Graph visualisation dashboard."""

    def __init__(self) -> None:
        self.visualizer = WorkflowVisualizer()

    def ingest_event(self, event: Dict[str, Any]) -> None:
        """Ingest a structured event and update the graph."""
        data = event.get("data")
        if isinstance(data, dict):
            self.visualizer.add_event(data)

    def get_graph(self) -> Dict[str, Any]:
        return self.visualizer.export("json")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------


class EventModel(BaseModel):
    timestamp: datetime
    level: str
    message: str
    correlation_id: str
    event_type: str | None = None
    data: Dict[str, Any] | None = None


def create_cerebro_app(dashboard: CerebroDashboard | None = None) -> FastAPI:
    """Create a FastAPI app exposing Cerebro endpoints."""

    dashboard = dashboard or CerebroDashboard()
    app = FastAPI()

    @app.post("/event")
    def post_event(event: EventModel) -> Dict[str, str]:
        dashboard.ingest_event(event.model_dump())
        return {"status": "ok"}

    @app.get("/graph")
    def get_graph() -> Dict[str, Any]:
        return dashboard.get_graph()

    return app


__all__ = ["CerebroDashboard", "create_cerebro_app"]
