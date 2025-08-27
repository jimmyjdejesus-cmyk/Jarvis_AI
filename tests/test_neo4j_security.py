from app.main import app

import jarvis.memory.project_memory as project_memory
from jarvis.memory.memory_bus import MemoryBus
from jarvis.memory.project_memory import ProjectMemory
from unittest.mock import MagicMock, patch

import pytest

from jarvis.world_model.neo4j_graph import Neo4jGraph


def test_credentials_loaded_from_env(monkeypatch):
    monkeypatch.setenv("NEO4J_URI", "bolt://neo4j.test")
    monkeypatch.setenv("NEO4J_USER", "user")
    monkeypatch.setenv("NEO4J_PASSWORD", "secret")
    with patch("neo4j_graph.GraphDatabase.driver") as mock_driver:
        Neo4jGraph()
        mock_driver.assert_called_once_with("bolt://neo4j.test", auth=("user", "secret"))


def test_add_edge_rejects_invalid_relationship():
    graph = Neo4jGraph(driver=MagicMock())
    with pytest.raises(ValueError):
        graph.add_edge("a", "b", "end-1")


def test_add_edge_runs_with_valid_relationship():
    driver = MagicMock()
    graph = Neo4jGraph(driver=driver)
    graph.add_edge("a", "b", "knows")
    driver.session.return_value.__enter__.return_value.run.assert_called_once()
