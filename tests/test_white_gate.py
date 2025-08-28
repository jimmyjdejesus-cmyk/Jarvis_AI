import importlib.util
import pathlib
import sys
import types
from typing import Any, Dict

import pytest

from jarvis.critics import CriticVerdict


def _load_graph_module(monkeypatch):
    root = pathlib.Path(__file__).resolve().parents[1] / "jarvis"

    jarvis_stub = types.ModuleType("jarvis")
    jarvis_stub.__path__ = [str(root)]
    monkeypatch.setitem(sys.modules, "jarvis", jarvis_stub)

    orch_stub = types.ModuleType("jarvis.orchestration")
    orch_stub.__path__ = [str(root / "orchestration")]
    monkeypatch.setitem(sys.modules, "jarvis.orchestration", orch_stub)

    team_agents_stub = types.ModuleType("jarvis.orchestration.team_agents")

    class OrchestratorAgent:  # pragma: no cover - stub
        pass

    class TeamMemberAgent:  # pragma: no cover - stub
        pass

    team_agents_stub.OrchestratorAgent = OrchestratorAgent
    team_agents_stub.TeamMemberAgent = TeamMemberAgent
    monkeypatch.setitem(
        sys.modules, "jarvis.orchestration.team_agents", team_agents_stub
    )

    pruning_stub = types.ModuleType("jarvis.orchestration.pruning")

    class PruningEvaluator:  # pragma: no cover - stub
        def should_prune(self, *args, **kwargs):
            return False

        async def evaluate(self, *args, **kwargs):  # pragma: no cover - stub
            return None

    pruning_stub.PruningEvaluator = PruningEvaluator
    monkeypatch.setitem(
        sys.modules, "jarvis.orchestration.pruning", pruning_stub
    )

    sys.modules.pop("langgraph", None)
    sys.modules.pop("langgraph.graph", None)
    sys.modules.pop("networkx", None)

    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.graph", root / "orchestration" / "graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


class DummyAgent:
    def __init__(self, team: str, result: Any):
        self.team = team
        self.result = result
        self.called = False

    def log(self, message: str, data: Dict[str, Any] | None = None):
        pass

    def run(self, objective: str, context: Dict[str, Any]):
        self.called = True
        return self.result


class DummyOrchestrator:
    def __init__(self, teams):
        self.teams = teams
        self.team_status = {
            name: "running"
            for name in ["Red", "Blue", "Yellow", "Green", "White", "Black"]
        }

    def log(self, message: str, data: Dict[str, Any] | None = None):
        pass

    def broadcast(self, message: str, data: Dict[str, Any] | None = None):
        pass


@pytest.fixture
def build_orchestrator(monkeypatch):
    module = _load_graph_module(monkeypatch)
    MultiTeamOrchestrator = module.MultiTeamOrchestrator

    def _builder(red_verdict: CriticVerdict, blue_verdict: CriticVerdict):
        red_agent = DummyAgent("Red", red_verdict)
        blue_agent = DummyAgent("Blue", blue_verdict)
        yellow_agent = DummyAgent("Yellow", {})
        green_agent = DummyAgent("Green", {})
        black_agent = DummyAgent("Black", {})
        white_agent = DummyAgent("White", {})
        orch = DummyOrchestrator(
            {
                module.ADVERSARY_PAIR_TEAM: (red_agent, blue_agent),
                module.COMPETITIVE_PAIR_TEAM: (yellow_agent, green_agent),
                module.SECURITY_QUALITY_TEAM: white_agent,
                module.INNOVATORS_DISRUPTORS_TEAM: black_agent,
            }
        )
        return MultiTeamOrchestrator(orch), black_agent

    return _builder


def test_white_gate_blocks_downstream_when_rejected(build_orchestrator):
    red_verdict = CriticVerdict(approved=False, fixes=[], risk=0.2, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, black_agent = build_orchestrator(red_verdict, blue_verdict)
    orchestrator.run("test objective")
    assert not black_agent.called


def test_white_gate_allows_downstream_when_approved(build_orchestrator):
    red_verdict = CriticVerdict(approved=True, fixes=[], risk=0.0, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, black_agent = build_orchestrator(red_verdict, blue_verdict)
    orchestrator.run("test objective")
    assert black_agent.called
