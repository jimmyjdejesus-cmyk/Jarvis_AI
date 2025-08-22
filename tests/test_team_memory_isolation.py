import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from jarvis.orchestration.agents import MetaAgent


def test_team_memory_isolated(tmp_path):
    meta = MetaAgent(directory=tmp_path)
    proj_dir = tmp_path / "proj"
    orch = meta.spawn_orchestrator("demo", directory=str(proj_dir))
    orch.run()

    red_log = Path(proj_dir, "red", "agent.md").read_text()
    blue_log = Path(proj_dir, "blue", "agent.md").read_text()

    assert "Red" in red_log
    assert "Blue" not in red_log
    assert "Blue" in blue_log
    assert "Red" not in blue_log

    # shared docs channel should exist
    assert Path(proj_dir, "shared_docs", "agent.md").exists()
