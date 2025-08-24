"""Real-time visualization and performance dashboard for Jarvis (Cerebro).

This module combines features from ``v2.agent.adapters.langgraph_ui`` and
``ui.visualizer`` to provide a lightweight web API that exposes a workflow
visualization and live performance metrics.  Events are expected to follow the
structure defined in ``schemas/event.json`` where the ``data`` field contains
node information understood by :class:`WorkflowVisualizer`.

The dashboard also tracks benchmark performance.  Metrics are recorded through
:func:`legacy.agent.core.performance_monitor.get_performance_monitor` which
allows historical analysis and aligns with ``BenchmarkRewardAgent`` outputs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from v2.agent.adapters.langgraph_ui import WorkflowVisualizer
from legacy.agent.core.performance_monitor import get_performance_monitor


class PerformanceTracker:
    """Track reward, token cost and probe policy counts."""

    def __init__(self) -> None:
        self.monitor = get_performance_monitor()
        self.total_reward = 0.0
        self.total_tokens = 0
        self.total_probes = 0
        self.tasks = 0

    def record(self, reward: float, tokens: int, probes: int) -> None:
        self.tasks += 1
        self.total_reward += reward
        self.total_tokens += tokens
        self.total_probes += probes

        # Persist metrics in the legacy performance monitor
        self.monitor.record_metric("reward", reward, "score")
        self.monitor.record_metric("tokens", float(tokens), "tokens")
        self.monitor.record_metric("probes", float(probes), "count")

    def summary(self) -> Dict[str, float]:
        return {
            "average_reward": self.total_reward / self.tasks if self.tasks else 0.0,
            "average_tokens": self.total_tokens / self.tasks if self.tasks else 0.0,
            "probe_policies": self.total_probes,
            "tasks": self.tasks,
        }


class CerebroDashboard:
    """Combine graph visualisation and performance metrics."""

    def __init__(self) -> None:
        self.visualizer = WorkflowVisualizer()
        self.performance = PerformanceTracker()

    def ingest_event(self, event: Dict[str, Any]) -> None:
        """Ingest a structured event and update the graph."""
        data = event.get("data")
        if isinstance(data, dict):
            self.visualizer.add_event(data)

    def get_graph(self) -> Dict[str, Any]:
        return self.visualizer.export("json")

    def record_performance(self, reward: float, tokens: int, probes: int) -> None:
        self.performance.record(reward, tokens, probes)

    def get_performance(self) -> Dict[str, float]:
        return self.performance.summary()


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


class PerformanceModel(BaseModel):
    reward: float
    tokens: int
    probes: int


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

    @app.post("/performance")
    def post_performance(perf: PerformanceModel) -> Dict[str, str]:
        dashboard.record_performance(perf.reward, perf.tokens, perf.probes)
        return {"status": "ok"}

    @app.get("/performance")
    def get_performance() -> Dict[str, float]:
        return dashboard.get_performance()

    return app


__all__ = ["CerebroDashboard", "PerformanceTracker", "create_cerebro_app"]
