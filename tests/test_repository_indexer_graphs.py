from pathlib import Path

import pytest
import importlib.util
import types
import sys

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[misc]
    return module


kg_mod = _load_module(
    "knowledge_graph", ROOT / "jarvis" / "world_model" / "knowledge_graph.py"
)
neo_mod = _load_module(
    "neo4j_graph", ROOT / "jarvis" / "world_model" / "neo4j_graph.py"
)

jarvis_pkg = types.ModuleType("jarvis")
world_pkg = types.ModuleType("jarvis.world_model")
world_pkg.knowledge_graph = kg_mod
world_pkg.neo4j_graph = neo_mod
jarvis_pkg.world_model = world_pkg
sys.modules["jarvis"] = jarvis_pkg
sys.modules["jarvis.world_model"] = world_pkg
sys.modules["jarvis.world_model.knowledge_graph"] = kg_mod
sys.modules["jarvis.world_model.neo4j_graph"] = neo_mod

RepositoryIndexer = _load_module(
    "repository_indexer", ROOT / "jarvis" / "tools" / "repository_indexer.py"
).RepositoryIndexer
KnowledgeGraph = kg_mod.KnowledgeGraph
Neo4jGraph = neo_mod.Neo4jGraph


def test_repository_indexer_builds_flow_graphs(tmp_path: Path):
    code = """
def foo(x):
    a = x + 1
    if a > 0:
        return a
    return 0
"""
    (tmp_path / "mod.py").write_text(code)
    kg = KnowledgeGraph()
    idx = RepositoryIndexer(repo_path=tmp_path)
    idx.index_repository(kg)

    func_node = "mod.py::foo"
    data = kg.graph.nodes[func_node]
    assert data["ast"].startswith("FunctionDef")
    assert any(edge[0] == data["cfg"][0][0] for edge in data["cfg"])
    assert any(var == "a" for _, _, var in data["dfg"])


def test_neo4j_graph_adds_nodes_and_edges():
    class DummySession:
        def __init__(self):
            self.queries = []

        def run(self, query, **params):
            self.queries.append((query, params))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    class DummyDriver:
        def __init__(self):
            self.session_obj = DummySession()

        def session(self):
            return self.session_obj

        def close(self):
            pass

    driver = DummyDriver()
    graph = Neo4jGraph(driver=driver)  # type: ignore[arg-type]
    graph.add_node("n1", "file", {"path": "n1"})
    graph.add_edge("n1", "n2", "contains")

    assert driver.session_obj.queries[0][0].startswith("MERGE")
    assert "MATCH" in driver.session_obj.queries[1][0]
