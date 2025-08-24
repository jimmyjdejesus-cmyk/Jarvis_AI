import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jarvis.tools.repository_indexer import RepositoryIndexer
from jarvis.world_model.knowledge_graph import KnowledgeGraph


def test_index_repository_writes_graph(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "mod.py").write_text("def func():\n    pass\n")
    kg = KnowledgeGraph()
    index_dir = tmp_path / "index"
    indexer = RepositoryIndexer(repo_path=repo, index_dir=index_dir)
    indexer.index_repository(kg)
    graph_file = index_dir / f"graph_{indexer.version}.json"
    data = json.loads(graph_file.read_text())
    node_ids = {n["id"] for n in data["nodes"]}
    assert any("mod.py" in nid for nid in node_ids)
