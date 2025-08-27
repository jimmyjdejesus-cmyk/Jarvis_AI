"""Tests for key REST endpoints using FastAPI's TestClient."""

from fastapi.testclient import TestClient
import pytest
import types
import sys
import os

# Stub minimal jarvis modules to avoid heavy imports
neo_module = types.ModuleType("jarvis.world_model.neo4j_graph")
class Neo4jGraph:  # pragma: no cover - stub
    def __init__(self, *_, **__):
        pass
neo_module.Neo4jGraph = Neo4jGraph
sys.modules.setdefault("jarvis", types.ModuleType("jarvis"))
sys.modules.setdefault("jarvis.world_model", types.ModuleType("jarvis.world_model"))
sys.modules["jarvis.world_model.neo4j_graph"] = neo_module
sys.modules.setdefault("jarvis.workflows", types.ModuleType("jarvis.workflows"))
workflows_engine = types.ModuleType("jarvis.workflows.engine")
workflows_engine.workflow_engine = object()
sys.modules["jarvis.workflows.engine"] = workflows_engine

from app.main import app  # noqa: E402
from app.auth import get_current_user  # noqa: E402


@pytest.fixture
def client(mock_neo4j_graph):
    """Return a TestClient with authentication and API key overridden."""
    app.dependency_overrides[get_current_user] = lambda: {"username": "tester", "roles": []}
    os.environ["JARVIS_API_KEY"] = "test-key"
    return TestClient(app)


def test_knowledge_query_success(client, mock_neo4j_graph):
    """The knowledge query endpoint returns Neo4j results."""
    mock_neo4j_graph.query.return_value = [{"n": 1}]
    resp = client.post("/knowledge/query", json={"query": "MATCH (n) RETURN n"})
    assert resp.status_code == 200
    assert resp.json() == {"results": [{"n": 1}]}
    mock_neo4j_graph.query.assert_called_once_with("MATCH (n) RETURN n")


def test_mission_history_success(client, mock_neo4j_graph):
    """The mission history endpoint returns stored mission data."""
    mock_neo4j_graph.get_mission_history.return_value = {"id": "m1", "steps": []}
    resp = client.get("/missions/m1/history", headers={"X-API-Key": "test-key"})
    assert resp.status_code == 200
    assert resp.json() == {"id": "m1", "steps": []}
    mock_neo4j_graph.get_mission_history.assert_called_once_with("m1")
