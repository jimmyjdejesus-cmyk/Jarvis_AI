import importlib.util
import pathlib
import sys
import pytest

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "jarvis"
    / "world_model"
    / "neo4j_graph.py"
)
spec = importlib.util.spec_from_file_location("neo4j_graph", MODULE_PATH)
neo4j_graph = importlib.util.module_from_spec(spec)
sys.modules["neo4j_graph"] = neo4j_graph
spec.loader.exec_module(neo4j_graph)  # type: ignore[assignment]
Neo4jGraph = neo4j_graph.Neo4jGraph


class DummyRecord:
    def __init__(self, data):
        self._data = data

    def data(self):
        return self._data


class DummySession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def run(self, *args, **kwargs):
        return [DummyRecord({"n": 1})]


class DummyDriver:
    def session(self):
        return DummySession()


def test_read_only_cypher_allowed():
    graph = Neo4jGraph(driver=DummyDriver())
    result = graph.query("MATCH (n) RETURN n")
    assert result == [{"n": 1}]


@pytest.mark.parametrize(
    "query",
    [
        "CREATE (n)",
        "MATCH (n) RETURN n; MATCH (m) RETURN m",
        "MERGE (n {id: 1}) RETURN n",
        "DELETE n",
    ],
)
def test_disallowed_cypher_raises(query):
    graph = Neo4jGraph(driver=DummyDriver())
    with pytest.raises(ValueError):
        graph.query(query)
