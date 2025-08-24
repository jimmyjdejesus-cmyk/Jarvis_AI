import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jarvis.retrieval.graph_rag import build_graph, save_graph, load_graph


def test_build_and_persist_graph(tmp_path: Path) -> None:
    relationships = [("a", "b", "link"), ("b", "c", "link")]
    attrs = {"a": {"type": "start"}, "b": {"type": "mid"}, "c": {"type": "end"}}
    g = build_graph(relationships, attrs)
    graph_file = tmp_path / "graph.json"
    save_graph(g, graph_file)
    loaded = load_graph(graph_file)
    assert set(loaded.nodes()) == {"a", "b", "c"}
    assert ("a", "b") in loaded.edges()
    data = json.loads(graph_file.read_text())
    assert data["nodes"]
