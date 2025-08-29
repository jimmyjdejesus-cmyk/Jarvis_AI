"""Minimal API tests ensuring memory bus operations function."""

from pathlib import Path

from jarvis.memory.replay_memory import ReplayMemory, Experience


def test_push_and_recall(tmp_path):
    memory = ReplayMemory(capacity=10, log_dir=str(tmp_path))
    memory.add(Experience("s1", "a1", 1.0, "s2", False))
    memory.add(Experience("s1", "a2", 0.5, "s3", True))
    recalled = memory.recall("s1", top_k=2)
    assert len(recalled) == 2
    assert recalled[0].action == "a2"
    assert recalled[1].action == "a1"
    log_content = Path(tmp_path, "agent.md").read_text()
    assert "Inserted experience" in log_content
    assert "Recall experience" in log_content
