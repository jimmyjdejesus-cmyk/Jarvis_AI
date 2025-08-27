"""Tests for the knowledge query API error handling."""

from fastapi.testclient import TestClient
from unittest.mock import patch
from neo4j.exceptions import ServiceUnavailable, TransientError

from app.main import app


client = TestClient(app)


def test_knowledge_query_service_unavailable() -> None:
    """ServiceUnavailable from Neo4j results in HTTP 500."""
    with patch(
        "jarvis.world_model.neo4j_graph.Neo4jGraph.query",
        side_effect=ServiceUnavailable("database down"),
        create=True,
    ):
        response = client.post("/knowledge/query", json={"query": "MATCH (n) RETURN n"})
    assert response.status_code == 500
    assert "service" in response.json().get("detail", "").lower()


def test_knowledge_query_transient_error() -> None:
    """TransientError from Neo4j results in HTTP 500."""
    with patch(
        "jarvis.world_model.neo4j_graph.Neo4jGraph.query",
        side_effect=TransientError("temporary failure"),
        create=True,
    ):
        response = client.post("/knowledge/query", json={"query": "MATCH (n) RETURN n"})
    assert response.status_code == 500
    assert "transient" in response.json().get("detail", "").lower()
