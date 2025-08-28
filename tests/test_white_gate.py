from typing import Any, Dict

import pytest

from jarvis.critics import CriticVerdict
from tests.conftest import load_graph_module


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
    module = load_graph_module(monkeypatch)
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

    state = {

        "objective": "test",

        "context": {},

        "team_outputs": {},

        "critics": {},

    }
    state = orchestrator._run_adversary_pair(state)

    assert state["halt"]
    assert not black_agent.called


def test_white_gate_allows_downstream_when_approved(build_orchestrator):
    red_verdict = CriticVerdict(approved=True, fixes=[], risk=0.0, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
orchestrator, black_agent = build_orchestrator(red_verdict, blue_verdict)
    state = {
        "objective": "test",
        "context": {},
        "team_outputs": {},
        "critics": {},
    }
    state = orchestrator._run_adversary_pair(state)
    assert not state["halt"]
    orchestrator._run_innovators_disruptors(state)
    assert black_agent.called


def test_white_gate_accepts_dict_outputs(build_orchestrator):
    red_dict = {"approved": True, "risk": 0.0, "notes": ""}
    blue_dict = {"approved": True, "risk": 0.1, "notes": ""}
    orchestrator, black_agent, _white_agent = build_orchestrator(
        red_dict, blue_dict
    )
    result = orchestrator.run("objective")
    assert black_agent.called
    assert result["halt"] is False


def test_white_gate_handles_unexpected_output_type(build_orchestrator):
    red_output = "unexpected"
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, black_agent, _white_agent = build_orchestrator(
        red_output, blue_verdict
    )
    result = orchestrator.run("objective")
    assert not black_agent.called
    assert result["halt"] is True


def test_white_gate_calls_security_quality_always(build_orchestrator):
    red_verdict = CriticVerdict(approved=False, fixes=[], risk=0.2, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, _black_agent, white_agent = build_orchestrator(
        red_verdict, blue_verdict
    )
    orchestrator.run("objective")
    assert white_agent.called