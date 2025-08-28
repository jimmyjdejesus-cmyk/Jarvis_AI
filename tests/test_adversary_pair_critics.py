"""Tests for Red/Blue team critic integration in MultiTeamOrchestrator."""

from importlib import util
from pathlib import Path
import sys
import types

stub = types.ModuleType("jarvis.orchestration.team_agents")
stub_pruning = types.ModuleType("jarvis.orchestration.pruning")


class OrchestratorAgent:  # pragma: no cover - stub for import
    pass


class TeamMemberAgent:  # pragma: no cover - stub for import
    pass


stub.OrchestratorAgent = OrchestratorAgent
stub.TeamMemberAgent = TeamMemberAgent


class PruningEvaluator:  # pragma: no cover - stub for import
    def __init__(self, *a, **k):
        pass

    def should_prune(self, team):
        return False


stub_pruning.PruningEvaluator = PruningEvaluator
sys.modules["jarvis.orchestration.team_agents"] = stub
sys.modules["jarvis.orchestration.pruning"] = stub_pruning


spec = util.spec_from_file_location(
    "graph", Path("jarvis/orchestration/graph.py")
)
graph = util.module_from_spec(spec)
spec.loader.exec_module(graph)
MultiTeamOrchestrator = graph.MultiTeamOrchestrator


def test_adversary_pair_runs_with_critics():
    """Red and Blue outputs should be reviewed and stored in state."""

    class DummyTeam:
        def __init__(self, team, output):
            self.team = team
            self._output = output
            self.log = lambda *a, **k: None

        def run(self, objective, context):
            return self._output

    red_agent = DummyTeam("Red", "red output")
    blue_agent = DummyTeam("Blue", {"success": True})

    class DummyOrchestrator:
        def __init__(self):
            self.teams = {"adversary_pair": (red_agent, blue_agent)}
            self.team_status = {"Red": "running", "Blue": "running"}

        def log(self, *a, **k):  # pragma: no cover - simple stub
            pass

        def broadcast(self, *a, **k):  # pragma: no cover - simple stub
            pass

    orchestrator = DummyOrchestrator()
    mto = MultiTeamOrchestrator(orchestrator)

    state = {
        "objective": "obj",
        "context": {},
        "team_outputs": {},
        "critics": {},
        "next_team": "",
    }

    result = mto._run_adversary_pair(state)

    assert "adversary_pair" in result["team_outputs"]
    assert result["critics"]["red"].notes == "No MCP client configured"
    assert result["critics"]["blue"].approved is True
