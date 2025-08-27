import random
from dataclasses import dataclass
from app.main import app

import jarvis.memory.project_memory as project_memory
from jarvis.memory.memory_bus import MemoryBus
from jarvis.memory.project_memory import ProjectMemory
from jarvis.memory.replay_memory import ReplayMemory


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
