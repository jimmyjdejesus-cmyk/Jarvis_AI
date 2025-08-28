from pathlib import Path

from jarvis.orchestration.black_team_orchestrator import BlackTeamOrchestrator
from jarvis.memory.memory_bus import MemoryBus


def test_black_team_orchestrator_filters_context(tmp_path):
    shared_bus = MemoryBus(tmp_path)
    orch = BlackTeamOrchestrator("disrupt market", directory=tmp_path, shared_bus=shared_bus)
    tasks = [
        {
            "id": "t1",
            "description": "probe defenses",
            "context": {"disrupt_signal": "yes", "noise": "ignore"},
        }
    ]
    results = orch.run_mission(tasks)
    strategy = results[0]["output"]["strategy"]
    assert "disrupt_signal" in strategy
    assert "noise" not in strategy
    # ensure log written to shared bus
    log_text = Path(shared_bus.log_file).read_text()
    assert "Completed probe defenses" in log_text
