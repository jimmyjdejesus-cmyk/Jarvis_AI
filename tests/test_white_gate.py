from typing import Any, Dict

from jarvis.critics import CriticVerdict
from jarvis.orchestration.graph import MultiTeamOrchestrator


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


def build_orchestrator(
    red_verdict: CriticVerdict, blue_verdict: CriticVerdict
):
    red_agent = DummyAgent("Red", red_verdict)
    blue_agent = DummyAgent("Blue", blue_verdict)
    yellow_agent = DummyAgent("Yellow", {})
    green_agent = DummyAgent("Green", {})
    black_agent = DummyAgent("Black", {})
    white_agent = DummyAgent("White", {})
    orch = DummyOrchestrator(
        {
            "adversary_pair": (red_agent, blue_agent),
            "competitive_pair": (yellow_agent, green_agent),
            "security_quality": white_agent,
            "innovators_disruptors": black_agent,
        }
    )
    return MultiTeamOrchestrator(orch), black_agent


def test_white_gate_blocks_downstream_when_rejected():
    red_verdict = CriticVerdict(approved=False, fixes=[], risk=0.2, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, black_agent = build_orchestrator(red_verdict, blue_verdict)
    orchestrator.run("test objective")
    assert not black_agent.called


def test_white_gate_allows_downstream_when_approved():
    red_verdict = CriticVerdict(approved=True, fixes=[], risk=0.0, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, black_agent = build_orchestrator(red_verdict, blue_verdict)
    orchestrator.run("test objective")
    assert black_agent.called
