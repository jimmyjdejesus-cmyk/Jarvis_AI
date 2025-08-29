from pathlib import Path
from typing import Any, Dict

from jarvis.orchestration.black_team_orchestrator import BlackTeamOrchestrator
from jarvis.orchestration.graph import MultiTeamOrchestrator
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


def test_white_team_outputs_excluded_from_black_context():
    """Ensure White team outputs are not visible to the Black team."""

    captured_context: Dict[str, Any] = {}

    class RecordingAgent:
        team = "Black"

        def log(self, message: str, data: Dict[str, Any] | None = None):
            pass

        def run(self, objective: str, context: Dict[str, Any]):
            nonlocal captured_context
            captured_context = context
            return {}

    black_agent = RecordingAgent()

    class DummyOrchestrator:
        def __init__(self):
            self.teams = {"innovators_disruptors": black_agent}
            self.team_status = {name: "running" for name in [
                "Red",
                "Blue",
                "Yellow",
                "Green",
                "White",
                "Black",
            ]}

        def log(self, message: str, data: Dict[str, Any] | None = None):
            pass

        def broadcast(self, message: str, data: Dict[str, Any] | None = None):
            pass

    orchestrator = MultiTeamOrchestrator(DummyOrchestrator())
    state = {
        "objective": "test",
        "context": {"info": "public", "security_quality": "secret"},
        "team_outputs": {"security_quality": {"report": "top secret"}},
        "critics": {},
        "next_team": "innovators_disruptors",
    }

    orchestrator._run_innovators_disruptors(state)

    assert "security_quality" not in captured_context
    assert captured_context["info"] == "public"
