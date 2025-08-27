from collections import Counter
import importlib.util
import random
import sys
import types
from pathlib import Path

# Manually construct lightweight package structure so that replay_memory
# can resolve its relative imports without executing the heavy jarvis package.
repo_root = Path(__file__).resolve().parents[1]
jarvis_path = repo_root / "jarvis"
memory_path = jarvis_path / "memory"

jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(jarvis_path)]
sys.modules["jarvis"] = jarvis_pkg

memory_pkg = types.ModuleType("jarvis.memory")
memory_pkg.__path__ = [str(memory_path)]
sys.modules["jarvis.memory"] = memory_pkg


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_load(
    "jarvis.memory.memory_bus", memory_path / "memory_bus.py"
)
replay_module = _load(
    "jarvis.memory.replay_memory", memory_path / "replay_memory.py"
)

Experience = replay_module.Experience
ReplayMemory = replay_module.ReplayMemory


def test_ring_buffer_behavior(tmp_path):
    mem = ReplayMemory(capacity=2, log_dir=str(tmp_path))
    mem.add(Experience("s1", 0, 0.0, "s2", False))
    mem.add(Experience("s2", 0, 0.0, "s3", False))
    mem.add(Experience("s3", 0, 0.0, "s4", False))
    assert len(mem) == 2
    states = {exp.state for exp in mem._storage}
    assert states == {"s2", "s3"}


def test_prioritized_sampling(tmp_path):
    random.seed(0)
    mem = ReplayMemory(capacity=3, log_dir=str(tmp_path))
    mem.add(Experience(1, 0, 0.0, 2, False), priority=1.0)
    mem.add(Experience(2, 0, 0.0, 3, False), priority=100.0)
    mem.add(Experience(3, 0, 0.0, 4, False), priority=1.0)
    counts = Counter()
    for _ in range(200):
        sample = mem.sample(1)[0]
        counts[sample.state] += 1
    assert counts[2] > counts[1] and counts[2] > counts[3]
