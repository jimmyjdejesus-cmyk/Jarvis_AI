import sys
import pathlib
import random
import os
from collections import deque
from dataclasses import dataclass
from typing import List, Any
import pytest
import unittest
from unittest.mock import patch
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

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
from memory.replay_memory import ReplayMemory


@dataclass
class Experience:
    state: int
    action: int
    reward: float


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


class TestAPI(unittest.TestCase):

    def setUp(self):
        os.environ["JARVIS_API_KEY"] = "test-key"
        self.client = TestClient(app)
        self.headers = {"X-API-Key": "test-key"}

    @patch('app.main.workflow_engine')
    def test_get_workflow_status_found(self, mock_workflow_engine):
        mock_workflow_engine.get_workflow_status.return_value = {
            "workflow_id": "test_id",
            "status": "completed",
        }
        response = self.client.get("/api/workflow/status/test_id", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")
        mock_workflow_engine.get_workflow_status.assert_called_once_with("test_id")

    @patch('app.main.workflow_engine')
    def test_get_workflow_status_not_found(self, mock_workflow_engine):
        mock_workflow_engine.get_workflow_status.return_value = None
        response = self.client.get("/api/workflow/status/not_found_id", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        mock_workflow_engine.get_workflow_status.assert_called_once_with("not_found_id")

    def test_api_key_required(self):
        response = self.client.get("/api/workflow/status/test_id")
        self.assertEqual(response.status_code, 401)


def test_buffer_capacity():
    mem = ReplayMemory(capacity=3)
    for i in range(4):
        mem.push(Experience(i, i, float(i)))
    assert len(mem.buffer) == 3
    states = [exp.state for exp, _ in mem.buffer]
    assert 0 not in states  # oldest dropped


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


def test_push_and_recall(tmp_path):
    bus = MemoryBus(tmp_path)
    memory = ReplayMemory(capacity=10, memory_bus=bus)
    memory.push("s1", "a1", 1.0, "s2", False)
    memory.push("s1", "a2", 0.5, "s3", True)
    recalled = memory.recall("s1", top_k=2)
    assert len(recalled) == 2
    assert recalled[0][1] == "a2"
    assert recalled[1][1] == "a1"
    log_content = bus.read_log()
    assert "push" in log_content
    assert "recall" in log_content

if __name__ == '__main__':
    unittest.main()