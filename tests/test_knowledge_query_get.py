"""Tests for knowledge and health endpoints including negative cases."""

from unittest.mock import patch
import types
import sys
from fastapi.testclient import TestClient

# Stub minimal jarvis package to avoid heavy imports during import
neo_module = types.ModuleType("jarvis.world_model.neo4j_graph")


class Neo4jGraph:  # type: ignore[override]
    def __init__(self, *_, **__):
        pass


neo_module.Neo4jGraph = Neo4jGraph
sys.modules.setdefault("jarvis", types.ModuleType("jarvis"))
sys.modules.setdefault(
    "jarvis.world_model", types.ModuleType("jarvis.world_model")
)
sys.modules["jarvis.world_model.neo4j_graph"] = neo_module

sys.modules.setdefault(
    "jarvis.workflows", types.ModuleType("jarvis.workflows")
)
workflows_engine = types.ModuleType("jarvis.workflows.engine")
workflows_engine.workflow_engine = object()
sys.modules["jarvis.workflows.engine"] = workflows_engine


from app.main import app  # noqa: E402

client = TestClient(app)


def test_get_knowledge_query_success():
    """Valid queries return results from KnowledgeGraph."""
    with patch(
        "app.main.knowledge_graph.query",
        return_value=["n1"],
    ) as mock_query:
        response = client.get("/knowledge/query", params={"q": "nodes"})
    assert response.status_code == 200
    assert response.json() == {"results": ["n1"]}
    mock_query.assert_called_once_with("nodes")


def test_get_knowledge_query_bad_request():
    """Unsupported queries return HTTP 400."""
    with patch(
        "app.main.knowledge_graph.query",
        side_effect=ValueError("Unsupported query"),
    ):
        response = client.get("/knowledge/query", params={"q": "invalid"})
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


def test_get_knowledge_query_missing_param():
    """Missing query parameter returns validation error."""
    response = client.get("/knowledge/query")
    assert response.status_code == 422


def test_health_endpoint():
    """Health endpoint returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_post_unsupported_method():
    """POST requests return HTTP 405 for health endpoint."""
    response = client.post("/health")
    assert response.status_code == 405


def test_health_put_unsupported_method():
    """PUT requests return HTTP 405 for health endpoint."""
    response = client.put("/health")
    assert response.status_code == 405


def test_unknown_endpoint():
    """Requests to unknown paths return HTTP 404."""
    response = client.get("/unknown")
    assert response.status_code == 404


def test_knowledge_query_post_unsupported_method():
    """POST requests return HTTP 405 for knowledge query endpoint."""
    response = client.post("/knowledge/query", json={"q": "nodes"})
    assert response.status_code == 405


def test_knowledge_query_delete_unsupported_method():
    """DELETE requests return HTTP 405 for knowledge query endpoint."""
    response = client.delete("/knowledge/query")
    assert response.status_code == 405