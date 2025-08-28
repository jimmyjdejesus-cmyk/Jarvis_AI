import importlib.util
import pathlib
import sys
import types
import asyncio
import time

import pytest

from tests.conftest import load_graph_module


class DummyGraph:
    def stream(self, *_args, **_kwargs):
        return []


@pytest.fixture
def mto_cls(monkeypatch):
    """Load MultiTeamOrchestrator with stubbed dependencies."""
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

    pruning_stub.PruningEvaluator = PruningEvaluator
    monkeypatch.setitem(
        sys.modules, "jarvis.orchestration.pruning", pruning_stub
    )

    critics_stub = types.ModuleType("jarvis.critics")

    class CriticVerdict:  # pragma: no cover - stub
        pass

    class WhiteGate:  # pragma: no cover - stub
        def merge(self, red, blue):
            return CriticVerdict()

    class RedTeamCritic:  # pragma: no cover - stub
        async def review(self, *args, **kwargs):
            return CriticVerdict()

    class BlueTeamCritic:  # pragma: no cover - stub
        async def review(self, *args, **kwargs):
            return CriticVerdict()

    critics_stub.CriticVerdict = CriticVerdict
    critics_stub.WhiteGate = WhiteGate
    critics_stub.RedTeamCritic = RedTeamCritic
    critics_stub.BlueTeamCritic = BlueTeamCritic
    monkeypatch.setitem(sys.modules, "jarvis.critics", critics_stub)

    langgraph_stub = types.ModuleType("langgraph.graph")

    class StateGraph:  # pragma: no cover - stub
        def __init__(self, *args, **kwargs):
            pass

        def add_node(self, *args, **kwargs):
            pass

        def set_entry_point(self, *args, **kwargs):
            pass

        def add_edge(self, *args, **kwargs):
            pass

        def compile(self):
            return self

        def stream(self, *_args, **_kwargs):
            return []

    langgraph_stub.StateGraph = StateGraph
    langgraph_stub.END = object()
    monkeypatch.setitem(sys.modules, "langgraph.graph", langgraph_stub)
    langgraph_pkg = types.ModuleType("langgraph")
    langgraph_pkg.graph = langgraph_stub
    monkeypatch.setitem(sys.modules, "langgraph", langgraph_pkg)

    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.graph", root / "orchestration" / "graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)

    class DummyGraph:  # pragma: no cover - stub
        def stream(self, *_args, **_kwargs):
            return []

    monkeypatch.setattr(
        module.MultiTeamOrchestrator,
        "_build_graph",
        lambda self: DummyGraph(),
    )

    return module.MultiTeamOrchestrator


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
    def __init__(self):
        self.teams = {"black": DummyBlackAgent()}
        self.team_status = {}

    def log(self, *args, **kwargs):  # pragma: no cover - noop
        pass

    def broadcast(self, *args, **kwargs):  # pragma: no cover - noop
        pass


class DummyAgent:
    def __init__(self, team):
        self.team = team


class PairOrchestrator:
    def __init__(self):
        self.teams = {
            "competitive_pair": (
                DummyAgent("Yellow"),
                DummyAgent("Green"),
            )
        }
        self.team_status = {}

    def log(self, *args, **kwargs):  # pragma: no cover - noop
        pass

    def broadcast(self, *args, **kwargs):  # pragma: no cover - noop
        pass


def test_black_team_excludes_white_team_context(mto_cls):
    orchestrator = DummyOrchestrator()
    mto = mto_cls(orchestrator)
    state = {
        "objective": "test",
        "context": {"foo": "bar", "leak": "secret"},
        "team_outputs": {
            "white": {"leak": "classified"}
        },
    }

    mto._run_innovators_disruptors(state)

    received = orchestrator.teams["black"].received_context
    assert "leak" not in received
    assert received["foo"] == "bar"


@pytest.mark.parametrize("white_output", [None, "ok", [1, 2], 42])
def test_black_team_handles_non_dict_white_output(mto_cls, white_output):
    orchestrator = DummyOrchestrator()
    mto = mto_cls(orchestrator)
    state = {
        "objective": "test",
        "context": {"foo": "bar", "leak": "secret"},
        "team_outputs": {"white": white_output},
    }

    mto._run_innovators_disruptors(state)

    received = orchestrator.teams["black"].received_context
    assert received["leak"] == "secret"


def test_competitive_pair_runs_in_parallel(mto_cls):
    orchestrator = PairOrchestrator()
    mto = mto_cls(orchestrator)

    async def fake_run(team, state):
        await asyncio.sleep(0.1)
        return {team.team: "ok"}

    mto._run_team_async = fake_run
    state = {"objective": "test", "context": {}, "team_outputs": {}}
    start = time.perf_counter()
    mto._run_competitive_pair(state)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.2
    assert len(state["team_outputs"]["competitive_pair"]) == 2