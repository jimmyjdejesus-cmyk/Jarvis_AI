"""Tests for MultiTeamOrchestrator helper functions."""

import sys
import types

sys.modules["jarvis.orchestration.team_agents"] = types.SimpleNamespace(
    OrchestratorAgent=object, TeamMemberAgent=object
)

from jarvis.orchestration.graph import MultiTeamOrchestrator  # noqa: E402


def test_oracle_judge_prefers_higher_score():
    yellow = {"score": 0.5}
    green = {"score": 0.8}
    result = MultiTeamOrchestrator._oracle_judge(yellow, green)
    assert result["winner"] == "Green"
    assert result["scores"]["Yellow"] == 0.5
    assert result["scores"]["Green"] == 0.8
    assert result["winning_output"] == green
