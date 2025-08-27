from fastapi.testclient import TestClient
from unittest.mock import patch
from neo4j.exceptions import ServiceUnavailable, TransientError
import types
import sys

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
from jarvis.world_model.neo4j_graph import Neo4jGraph  # noqa: E402

client = TestClient(app)


def test_knowledge_query_service_unavailable():
    with patch.object(
        Neo4jGraph,
        "query",
        side_effect=ServiceUnavailable("down"),
        create=True,
    ):
        response = client.post(
            "/knowledge/query",
            json={"query": "MATCH (n) RETURN n"},
        )
    assert response.status_code == 500
    assert "service unavailable" in response.json()["detail"].lower()


def test_knowledge_query_transient_error():
    with patch.object(
        Neo4jGraph,
        "query",
        side_effect=TransientError("retry"),
        create=True,
    ):
        response = client.post(
            "/knowledge/query",
            json={"query": "MATCH (n) RETURN n"},
        )
    assert response.status_code == 500
    assert "transient error" in response.json()["detail"].lower()
