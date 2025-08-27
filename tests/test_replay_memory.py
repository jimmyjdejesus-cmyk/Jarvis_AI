import sys
import pathlib

# Ensure repository root on path for `jarvis` package
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import random
from collections import deque
from dataclasses import dataclass
from typing import List, Any

import pytest

# Import ProjectMemory without executing full jarvis package
import importlib.util

project_memory_spec = importlib.util.spec_from_file_location(
    "project_memory",
    pathlib.Path(__file__).resolve().parents[1] / "jarvis" / "memory" / "project_memory.py",
)
project_memory = importlib.util.module_from_spec(project_memory_spec)
sys.modules["project_memory"] = project_memory
project_memory_spec.loader.exec_module(project_memory)
ProjectMemory = project_memory.ProjectMemory


@dataclass
class Experience:
    state: int
    action: int
    reward: float


class ReplayMemory:
    """Simple replay memory with optional ProjectMemory backing."""

    def __init__(self, capacity: int, project_memory: ProjectMemory | None = None) -> None:
        self.capacity = capacity
        self.buffer: deque[tuple[Experience, float]] = deque(maxlen=capacity)
        self.project_memory = project_memory

    def push(self, exp: Experience, priority: float = 1.0) -> None:
        self.buffer.append((exp, priority))
        if self.project_memory:
            text = f"{exp.state}-{exp.action}-{exp.reward}"
            self.project_memory.add("proj", "sess", text)

    def sample(self, batch_size: int) -> List[Experience]:
        return [exp for exp, _ in random.sample(list(self.buffer), batch_size)]

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.buffer)


class PrioritizedReplayMemory(ReplayMemory):
    """Replay memory with priority-based sampling and updates."""

    def sample(self, batch_size: int) -> List[Experience]:
        priorities = [p for _, p in self.buffer]
        weights = [p / sum(priorities) for p in priorities]
        chosen = random.choices(list(self.buffer), weights=weights, k=batch_size)
        return [exp for exp, _ in chosen]

    def update_priorities(self, indices: List[int], priorities: List[float]) -> None:
        for idx, p in zip(indices, priorities):
            exp, _ = self.buffer[idx]
            self.buffer[idx] = (exp, p)


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
        mem.push(Experience(i, i, float(i)))
    assert len(mem.buffer) == 3
    states = [exp.state for exp, _ in mem.buffer]
    assert 0 not in states  # oldest dropped


def test_random_sampling():
    mem = ReplayMemory(capacity=5)
    for i in range(5):
        mem.push(Experience(i, i, float(i)))
    random.seed(0)
    batch = mem.sample(3)
    assert len(batch) == 3
    assert {e.state for e in batch}.issubset({0, 1, 2, 3, 4})


def test_priority_updates():
    mem = PrioritizedReplayMemory(capacity=5)
    for i in range(5):
        mem.push(Experience(i, i, float(i)))
    mem.update_priorities([0, 1], [0.1, 0.9])
    assert mem.buffer[0][1] == 0.1
    assert mem.buffer[1][1] == 0.9
    random.seed(1)
    batch = mem.sample(2)
    assert len(batch) == 2


def test_project_memory_recall(mock_project_memory: ProjectMemory):
    mem = ReplayMemory(capacity=3, project_memory=mock_project_memory)
    mem.push(Experience(1, 2, 3.0))
    results = mock_project_memory.query("proj", "sess", "1-2-3.0", top_k=1)
    assert results[0]["text"] == "1-2-3.0"