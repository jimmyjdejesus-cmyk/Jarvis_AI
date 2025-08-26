import os
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
spec_agents = importlib.util.spec_from_file_location(
    "jarvis.orchestration.agents", ROOT / "jarvis" / "orchestration" / "agents.py"
)
agents = importlib.util.module_from_spec(spec_agents)
sys.modules["jarvis.orchestration.agents"] = agents
spec_agents.loader.exec_module(agents)
MetaAgent = agents.MetaAgent


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
