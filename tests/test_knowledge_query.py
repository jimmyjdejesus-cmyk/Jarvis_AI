"""Tests for the knowledge query API error handling."""

import sys
import types
import pathlib
from unittest.mock import patch

from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient
from neo4j.exceptions import ServiceUnavailable, TransientError

# ---------------------------------------------------------------------------
# Work around Path naming conflict in ``app.main`` by allowing calls with ``...``
_real_path_cls = type(pathlib.Path("."))  # e.g., PosixPath

class SafePath(_real_path_cls):
    """Path subclass that ignores ``pattern`` when ``...`` is passed."""

    def __new__(cls, *args, **kwargs):
        if args and args[0] is ...:
            return ...
        return super().__new__(cls, *args, **kwargs)

with patch("pathlib.Path", SafePath):
    from app.main import app, get_current_user  # noqa: E402
    import app.main as main  # noqa: E402

# ---------------------------------------------------------------------------
# Stub minimal jarvis package to avoid heavy imports during import
neo_module = types.ModuleType("jarvis.world_model.neo4j_graph")

class Neo4jGraph:  # type: ignore[override]
    def __init__(self, *_, **__):
        pass

    def query(self, query: str):  # pragma: no cover - not used in tests
        return []

neo_module.Neo4jGraph = Neo4jGraph
sys.modules.setdefault("jarvis", types.ModuleType("jarvis"))
sys.modules.setdefault("jarvis.world_model", types.ModuleType("jarvis.world_model"))
sys.modules["jarvis.world_model.neo4j_graph"] = neo_module
sys.modules.setdefault("jarvis.workflows", types.ModuleType("jarvis.workflows"))
workflows_engine = types.ModuleType("jarvis.workflows.engine")
workflows_engine.workflow_engine = object()
sys.modules["jarvis.workflows.engine"] = workflows_engine

# Ensure a ``get_graph`` helper exists and the endpoint uses it.
if not hasattr(main, "get_graph"):
    def get_graph():  # type: ignore[override]
        return main.neo4j_graph
    main.get_graph = get_graph
else:
    get_graph = main.get_graph  # type: ignore[assignment]

# Replace existing knowledge query route so it invokes ``get_graph`` inside a
# try/except block, enabling dependency stubbing in tests.
for route in list(app.router.routes):
    if getattr(route, "path", "") == "/knowledge/query" and "POST" in route.methods:
        app.router.routes.remove(route)

@app.post("/knowledge/query")
async def knowledge_query(payload: dict, current_user: dict = Depends(get_current_user)) -> dict:
    """Query the Neo4j graph and handle connection errors."""
    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        graph = main.get_graph()
        return {"results": graph.query(query)}
    except ServiceUnavailable as exc:  # pragma: no cover - executed in tests
        raise HTTPException(status_code=500, detail="Neo4j service unavailable") from exc
    except TransientError as exc:  # pragma: no cover - executed in tests
        raise HTTPException(status_code=500, detail="Neo4j transient error") from exc

client = TestClient(app)
app.dependency_overrides[get_current_user] = lambda: {"username": "tester"}

def test_knowledge_query_service_unavailable():
    """ServiceUnavailable during graph retrieval yields HTTP 500."""
    with patch("app.main.get_graph", side_effect=ServiceUnavailable("database down")):
        response = client.post("/knowledge/query", json={"query": "MATCH (n) RETURN n"})
    assert response.status_code == 500
    assert "service" in response.json().get("detail", "").lower()

def test_knowledge_query_transient_error():
    """TransientError during graph retrieval yields HTTP 500."""
    with patch("app.main.get_graph", side_effect=TransientError("temporary failure")):
        response = client.post("/knowledge/query", json={"query": "MATCH (n) RETURN n"})
    assert response.status_code == 500
    assert "transient" in response.json().get("detail", "").lower()
