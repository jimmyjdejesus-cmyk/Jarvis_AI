from pathlib import Path
import importlib.util
import pytest
from unittest.mock import MagicMock

neo4j_path = Path(__file__).resolve().parents[1] / "jarvis" / "world_model" / "neo4j_graph.py"
spec = importlib.util.spec_from_file_location("neo4j_graph", neo4j_path)
neo4j_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(neo4j_module)
Neo4jGraph = neo4j_module.Neo4jGraph


def test_get_mission_history_sanitizes_and_filters():
    driver = MagicMock()
    session = driver.session.return_value.__enter__.return_value
    session.run.return_value.single.return_value = {
        "m": {"id": "m1", "name": "Mission", "password": "secret"},
        "steps": [{"id": "s1", "token": "abc"}],
        "facts": [{"id": "f1", "detail": "info", "secret": "x"}],
    }

    graph = Neo4jGraph(driver=driver)
    history = graph.get_mission_history("m1")

    assert history["mission"] == {"id": "m1", "name": "Mission"}
    assert history["steps"] == [{"id": "s1"}]
    assert history["facts"] == [{"id": "f1", "detail": "info"}]


def test_get_mission_history_invalid_id():
    graph = Neo4jGraph(driver=MagicMock())
    with pytest.raises(ValueError):
        graph.get_mission_history("bad id!")


def test_is_alive_true():
    driver = MagicMock()
    graph = Neo4jGraph(driver=driver)
    assert graph.is_alive()
    driver.verify_connectivity.assert_called_once()


def test_is_alive_false():
    driver = MagicMock()
    driver.verify_connectivity.side_effect = Exception("boom")
    graph = Neo4jGraph(driver=driver)
    assert not graph.is_alive()
