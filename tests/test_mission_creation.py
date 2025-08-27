import os
import importlib.util
import pathlib

import pytest
from fastapi.testclient import TestClient

spec = importlib.util.spec_from_file_location(
    "meta_intelligence", pathlib.Path(__file__).resolve().parents[1] / "jarvis/ecosystem/meta_intelligence.py"
)
mi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mi)
from jarvis.workflows.engine import WorkflowStatus
mi.WorkflowStatus = WorkflowStatus


class DummyGraph:
    def __init__(self):
        self.nodes = []

    def is_alive(self) -> bool:
        return True

    def add_node(self, node_id: str, node_type: str, attributes=None):
        self.nodes.append((node_id, node_type, attributes))


@pytest.fixture
def client(monkeypatch):
    os.environ["JARVIS_API_KEY"] = "test-key"

    async def noop():
        return None

    monkeypatch.setattr(mi, "initialize_cerebro", noop)
    graph = DummyGraph()
    monkeypatch.setattr(mi, "neo4j_graph", graph)
    with TestClient(mi.app) as test_client:
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
