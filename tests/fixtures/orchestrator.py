"""Fixtures and helpers for WhiteGate tests."""
from typing import Any, Dict, Tuple

import pytest
from jarvis.orchestration.graph import MultiTeamOrchestrator


class DummyAgent:
    """Record calls and return a preset result."""

    def __init__(self, team: str, result: Any):
        self.team = team
        self.result = result
        self.called = False

    def log(self, message: str, data: Dict[str, Any] | None = None) -> None:
        """No-op log method used by tests."""

    def run(self, objective: str, context: Dict[str, Any]) -> Any:
        """Record invocation and return preset result."""
        self.called = True
        return self.result


class DummyOrchestrator:
    """Container for team assignments used by tests."""

    def __init__(self, teams: Dict[str, Any]):
        self.teams = teams
        self.team_status = {
            name: "running"
            for name in ["Red", "Blue", "Yellow", "Green", "White", "Black"]
        }

    def log(self, message: str, data: Dict[str, Any] | None = None) -> None:
        """No-op orchestrator log."""

    def broadcast(
        self, message: str, data: Dict[str, Any] | None = None
    ) -> None:
        """No-op broadcast used by tests."""


@pytest.fixture
def build_orchestrator_with_critic_outputs() -> Any:
    """Build a MultiTeamOrchestrator with configurable critic outputs."""

    def _build(
        red_output: Any, blue_output: Any
    ) -> Tuple[MultiTeamOrchestrator, DummyAgent, DummyAgent]:
        red_agent = DummyAgent("Red", red_output)
        blue_agent = DummyAgent("Blue", blue_output)
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
        return MultiTeamOrchestrator(orch), black_agent, white_agent

    return _build
