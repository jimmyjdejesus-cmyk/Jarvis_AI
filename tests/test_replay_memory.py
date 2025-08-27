import sys
import pathlib
import random
from collections import deque
from dataclasses import dataclass
from typing import List, Any
import pytest
from pathlib import Path

# Ensure repository root on path for `jarvis` package
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / "jarvis"))

# Import ProjectMemory without executing the full jarvis package
import importlib.util

project_memory_spec = importlib.util.spec_from_file_location(
    "project_memory",
    pathlib.Path(__file__).resolve().parents[1] / "jarvis" / "memory" / "project_memory.py",
)
project_memory = importlib.util.module_from_spec(project_memory_spec)
sys.modules["project_memory"] = project_memory
project_memory_spec.loader.exec_module(project_memory)
ProjectMemory = project_memory.ProjectMemory

from memory.memory_bus import MemoryBus
from memory.replay_memory import ReplayMemory, Experience




class PrioritizedReplayMemory(ReplayMemory):
    """Replay memory with priority-based sampling and updates."""

    def sample(self, batch_size: int) -> List[Experience]:
        priorities = [exp.priority for exp in self._storage]
        weights = [p / sum(priorities) for p in priorities]
        chosen = random.choices(self._storage, weights=weights, k=batch_size)
        return chosen

    def update_priorities(self, indices: List[int], priorities: List[float]) -> None:
        for idx, p in zip(indices, priorities):
            self._storage[idx].priority = p


@pytest.fixture
def mock_project_memory(monkeypatch, tmp_path):
    class DummyCollection:
        def __init__(self) -> None:
            self.docs: List[str] = []
            self.metas: List[dict[str, Any]] = []

        def add(self, ids: List[str], documents: List[str], metadatas: List[dict[str, Any]]):
            self.docs.extend(documents)
            self.metas.extend(metadatas)

        def query(self, query_texts: List[str], n_results: int):
            return {"documents": [self.docs[:n_results]], "metadatas": [self.metas[:n_results]]}

    class DummyClient:
        def __init__(self, path: str) -> None:
            self.collection = DummyCollection()

        def get_or_create_collection(self, name: str, embedding_function: Any):
            return self.collection

    dummy_chroma = type("chroma", (), {"PersistentClient": DummyClient})
    dummy_embed = type("embed", (), {"EmbeddingFunction": object})
    monkeypatch.setattr(project_memory, "chromadb", dummy_chroma)
    monkeypatch.setattr(project_memory, "embedding_functions", dummy_embed)
    return ProjectMemory(persist_directory=str(tmp_path))


def test_buffer_capacity():
    mem = ReplayMemory(capacity=3)
    for i in range(4):
        mem.add(Experience(i, i, float(i), i+1, False))
    assert len(mem) == 3
    states = [exp.state for exp in mem._storage]
    assert 0 not in states  # oldest dropped


def test_random_sampling():
    mem = ReplayMemory(capacity=5)
    for i in range(5):
        mem.add(Experience(i, i, float(i), i+1, False))
    random.seed(0)
    batch = mem.sample(3)
    assert len(batch) == 3
    assert {e.state for e in batch}.issubset({0, 1, 2, 3, 4})


def test_priority_updates():
    mem = PrioritizedReplayMemory(capacity=5)
    for i in range(5):
        mem.add(Experience(i, i, float(i), i+1, False))
    mem.update_priorities([0, 1], [0.1, 0.9])
    assert mem._storage[0].priority == 0.1
    assert mem._storage[1].priority == 0.9
    random.seed(1)
    batch = mem.sample(2)
    assert len(batch) == 2


def test_push_and_recall(tmp_path):
    bus = MemoryBus(str(tmp_path))
    memory = ReplayMemory(capacity=10, log_dir=str(tmp_path))
    memory.add(Experience(state="s1", action="a1", reward=1.0, next_state="s2", done=False))
    memory.add(Experience(state="s1", action="a2", reward=0.5, next_state="s3", done=True))
    recalled = memory.recall("s1", top_k=2)
    assert len(recalled) == 2
    assert recalled[0].action == "a2"
    assert recalled[1].action == "a1"
    log_content = bus.read_log()
    assert "Inserted experience" in log_content
    assert "Recall experience" in log_content