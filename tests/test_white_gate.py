"""WhiteGate edge-case tests for MultiTeamOrchestrator."""

import pytest

from jarvis.critics import CriticVerdict
from tests.conftest import load_graph_module


class DummyAgent:
    """Minimal agent stub that records call status and returns canned output."""
    def __init__(self, team: str, output: "Any"):
        self.team = team
        self.output = output
        self.called = False

    def run(self, objective: str, context: dict) -> "Any":
        self.called = True
        return self.output

class DummyOrchestrator:
    """Minimal orchestrator stub with a predefined team structure."""
    def __init__(self, teams: dict):
        self.teams = teams
        self.team_status: dict[str, str] = {}

    def log(self, *args, **kwargs):
        pass

    def broadcast(self, *args, **kwargs):
        pass


@pytest.fixture
def build_orchestrator(monkeypatch):
    """Factory fixture to build a MultiTeamOrchestrator with mocked teams."""
    module = load_graph_module(monkeypatch)
    MultiTeamOrchestrator = module.MultiTeamOrchestrator

    def _builder(red_verdict: "Any", blue_verdict: "Any"):
        red_agent = DummyAgent("Red", red_verdict)
        blue_agent = DummyAgent("Blue", blue_verdict)
        black_agent = DummyAgent("Black", {})
        white_agent = DummyAgent("White", {})
        orch = DummyOrchestrator(
            {
                module.ADVERSARY_PAIR_TEAM: (red_agent, blue_agent),
                module.SECURITY_QUALITY_TEAM: white_agent,
                module.INNOVATORS_DISRUPTORS_TEAM: black_agent,
            }
        )
        # Return all agents needed for the various test assertions
        return MultiTeamOrchestrator(orch), black_agent, white_agent

    return _builder


def test_white_gate_blocks_downstream_when_rejected(build_orchestrator):
    """Red critic rejection should halt the graph."""
    red_verdict = CriticVerdict(approved=False, fixes=[], risk=0.2, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, black_agent, _ = build_orchestrator(red_verdict, blue_verdict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}
    
    final_state = orchestrator._run_adversary_pair(state)
    
    assert final_state.get("halt") is True


def test_white_gate_allows_downstream_when_approved(build_orchestrator):
    """Approval from both critics allows innovators to execute."""
    red_verdict = CriticVerdict(approved=True, fixes=[], risk=0.0, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, black_agent, _ = build_orchestrator(red_verdict, blue_verdict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}
    
    state = orchestrator._run_adversary_pair(state)
    assert not state.get("halt")
    
    orchestrator._run_innovators_disruptors(state)
    assert black_agent.called


def test_white_gate_accepts_dict_outputs(build_orchestrator):
    """Critic verdicts provided as dicts should be converted appropriately."""
    red_dict = {"approved": True, "risk": 0.0, "notes": ""}
    blue_dict = {"approved": True, "risk": 0.1, "notes": ""}
    orchestrator, _, _ = build_orchestrator(red_dict, blue_dict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}
    
    final_state = orchestrator._run_adversary_pair(state)
    
    assert final_state.get("halt") is False


def test_white_gate_handles_unexpected_output_type(build_orchestrator):
    """Non-dict/non-verdict outputs should cause rejection and halt."""
    red_output = "unexpected"
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, _, _ = build_orchestrator(red_output, blue_verdict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}

    final_state = orchestrator._run_adversary_pair(state)
    
    assert final_state.get("halt") is True
    assert "Unsupported output type" in final_state["critics"]["white_gate"]["notes"]


def test_white_gate_calls_security_quality_always(build_orchestrator):
    """The security-quality (White) agent should be callable even if the graph halts."""
    red_verdict = CriticVerdict(approved=False, fixes=[], risk=0.2, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, _, white_agent = build_orchestrator(red_verdict, blue_verdict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}
    
    # This test verifies behavior in the main `run` loop, not just a single step
    orchestrator.run("objective")
    
    assert white_agent.called


def test_white_gate_defaults_missing_fields(build_orchestrator):
    """Missing fields in a verdict dict should default to rejection without crashing."""
    red_dict = {}
    blue_dict = {"risk": 0.0}
    orchestrator, _, _ = build_orchestrator(red_dict, blue_dict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}

    final_state = orchestrator._run_adversary_pair(state)
    
    assert final_state.get("halt") is True


def test_white_gate_handles_malformed_verdict(build_orchestrator):
    """Invalid field types in a verdict dict should result in rejection."""
    red_dict = {"approved": True, "risk": "high"}  # risk should be a float
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.1, notes="")
    orchestrator, _, _ = build_orchestrator(red_dict, blue_verdict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}

    final_state = orchestrator._run_adversary_pair(state)
    
    assert final_state.get("halt") is True
    notes = final_state["critics"]["white_gate"]["notes"]
    assert "Malformed verdict structure" in notes
    assert final_state["critics"]["white_gate"]["risk"] == 1.0


def test_white_gate_propagates_critic_notes(build_orchestrator):
    """Notes from both critics should surface in the merged verdict."""
    red_verdict = CriticVerdict(approved=True, fixes=[], risk=0.0, notes="red note")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=0.0, notes="blue note")
    orchestrator, _, _ = build_orchestrator(red_verdict, blue_verdict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}

    final_state = orchestrator._run_adversary_pair(state)
    
    notes = final_state["critics"]["white_gate"]["notes"]
    assert "red note" in notes
    assert "blue note" in notes


def test_white_gate_handles_extreme_risk(build_orchestrator):
    """A high risk score should halt the workflow."""
    red_verdict = CriticVerdict(approved=True, fixes=[], risk=0.0, notes="")
    blue_verdict = CriticVerdict(approved=True, fixes=[], risk=10.0, notes="")
    orchestrator, _, _ = build_orchestrator(red_verdict, blue_verdict)
    state = {"objective": "test", "context": {}, "team_outputs": {}, "critics": {}}

    final_state = orchestrator._run_adversary_pair(state)
    
    assert final_state.get("halt") is True
    assert final_state["critics"]["white_gate"]["risk"] == 10.0