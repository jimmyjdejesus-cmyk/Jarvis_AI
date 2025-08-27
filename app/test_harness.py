"""Lightweight FastAPI test harness for endpoint testing.

This module exposes a ``create_test_app`` factory that builds a minimal
FastAPI application containing only the endpoints required for testing.
It avoids importing the production application, which pulls in heavy
Jarvis orchestrator modules that can cause side effects during tests.

The harness accepts a ``Neo4jGraph``-compatible object, allowing tests to
inject fakes or stubs to simulate database interactions without touching
real services.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Path


def create_test_app(graph: Optional[Any] = None) -> FastAPI:
    """Return a minimal FastAPI app for testing.

    Parameters
    ----------
    graph:
        Optional object implementing ``get_mission_history`` and
        ``is_alive``. Tests can provide a fake to avoid real database
        calls. When ``None``, a real ``Neo4jGraph`` is instantiated on
        demand.

    Returns
    -------
    FastAPI
        Application with the mission history and health endpoints.
    """

    if graph is None:  # pragma: no cover - exercised only in integration tests
        from jarvis.world_model.neo4j_graph import Neo4jGraph

        graph = Neo4jGraph()
    app = FastAPI()

    @app.get("/missions/{mission_id}/history")
    async def get_mission_history(
        mission_id: str = Path(..., regex=r"^[\w-]+$"),
    ) -> Dict[str, Any]:
        """Return mission history including steps and facts."""
        try:
            history = graph.get_mission_history(mission_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid mission id")

        if not history:
            raise HTTPException(status_code=404, detail="Mission not found")
        return history

    @app.get("/health")
    async def health() -> Dict[str, bool]:
        """Simple health check endpoint."""
        return {"neo4j_active": graph.is_alive()}

    return app
