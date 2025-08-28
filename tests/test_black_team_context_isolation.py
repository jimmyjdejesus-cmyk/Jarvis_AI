import time
import asyncio

import pytest

from tests.conftest import load_graph_module


class DummyGraph:
    def stream(self, *_args, **_kwargs):
        return []


@pytest.fixture
def graph_module(monkeypatch):
    module = load_graph_module(monkeypatch)
    monkeypatch.setattr(
        module.MultiTeamOrchestrator, "_build_graph", lambda self: DummyGraph()
    )
    return module


class DummyBlackAgent:
    team = "Black"

    def __init__(self):
        self.received_context = None

    def run(self, objective, context):
        self.received_context = context
        return {"status": "ok"}

    def log(self, message, data=None):  # pragma: no cover - noop
        pass


class DummyOrchestrator:
    def __init__(self, mod):
        self.teams = {mod.INNOVATORS_DISRUPTORS_TEAM: DummyBlackAgent()}
        self.team_status = {}

    def log(self, *args, **kwargs):  # pragma: no cover - noop
        pass

    def broadcast(self, *args, **kwargs):  # pragma: no cover - noop
        pass


class DummyAgent:
    def __init__(self, team):
        self.team = team


class PairOrchestrator:
    def __init__(self, mod):
        self.teams = {
            mod.COMPETITIVE_PAIR_TEAM: (
                DummyAgent("Yellow"),
                DummyAgent("Green"),
            )
        }
        self.team_status = {}

    def log(self, *args, **kwargs):  # pragma: no cover - noop
        pass

    def broadcast(self, *args, **kwargs):  # pragma: no cover - noop
        pass


def test_black_team_excludes_white_team_context(graph_module):
    orchestrator = DummyOrchestrator(graph_module)
    mto = graph_module.MultiTeamOrchestrator(orchestrator)
    state = {
        "objective": "test",
        "context": {"foo": "bar", "leak": "secret"},
        "team_outputs": {
            graph_module.SECURITY_QUALITY_TEAM: {"leak": "classified"}
        },
    }

    mto._run_innovators_disruptors(state)

    received = orchestrator.teams[
        graph_module.INNOVATORS_DISRUPTORS_TEAM
    ].received_context
    assert "leak" not in received
    assert received["foo"] == "bar"


@pytest.mark.parametrize("white_output", [None, "ok", [1, 2], 42])
def test_black_team_handles_non_dict_white_output(graph_module, white_output):
    orchestrator = DummyOrchestrator(graph_module)
    mto = graph_module.MultiTeamOrchestrator(orchestrator)
    state = {
        "objective": "test",
        "context": {"foo": "bar", "leak": "secret"},
        "team_outputs": {graph_module.SECURITY_QUALITY_TEAM: white_output},
    }

    mto._run_innovators_disruptors(state)

    received = orchestrator.teams[
        graph_module.INNOVATORS_DISRUPTORS_TEAM
    ].received_context
    assert received["leak"] == "secret"


def test_competitive_pair_runs_in_parallel(graph_module):
    orchestrator = PairOrchestrator(graph_module)
    mto = graph_module.MultiTeamOrchestrator(orchestrator)

    async def fake_run(team, state):
        await asyncio.sleep(0.1)
        return {team.team: "ok"}

    mto._run_team_async = fake_run
    state = {"objective": "test", "context": {}, "team_outputs": {}}
    start = time.perf_counter()
    mto._run_competitive_pair(state)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.2
    assert len(state["team_outputs"][graph_module.COMPETITIVE_PAIR_TEAM]) == 2
