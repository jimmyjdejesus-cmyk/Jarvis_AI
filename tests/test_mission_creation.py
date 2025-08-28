import os

import pytest
from fastapi.testclient import TestClient

from jarvis.workflows.engine import WorkflowStatus
import jarvis.agents.mission_planner as agent_mp
import app.main as main_app


class DummyGraph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node_id: str, node_type: str, attributes=None):
        self.nodes.append((node_id, node_type, attributes))


@pytest.fixture
def client(monkeypatch):
    os.environ["JARVIS_API_KEY"] = "test-key"

    # Avoid external LLM calls
    monkeypatch.setattr(
        agent_mp.model_client,
        "generate_response",
        lambda model, prompt: '{"tasks": ["test step"]}',
    )

    graph = DummyGraph()
    monkeypatch.setattr(main_app, "neo4j_graph", graph)
    with TestClient(main_app.app) as test_client:
        yield test_client, graph


def test_create_mission(client):
    test_client, graph = client
    payload = {"title": "Test Mission", "goal": "Test goal"}
    headers = {"X-API-Key": "test-key"}
    response = test_client.post("/api/missions", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == WorkflowStatus.PENDING.value
    assert graph.nodes
    assert graph.nodes[0][0] == data["mission_id"]
