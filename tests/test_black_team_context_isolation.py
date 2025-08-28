import importlib.util
import pathlib
import sys
import time
import types
import asyncio

import pytest


class DummyGraph:
    def stream(self, *_args, **_kwargs):
        return []


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

    # Ensure real langgraph/networkx are used
    sys.modules.pop("langgraph", None)
    sys.modules.pop("langgraph.graph", None)
    sys.modules.pop("networkx", None)

    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.graph", root / "orchestration" / "graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def graph_module(monkeypatch):
    module = _load_graph_module(monkeypatch)
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
