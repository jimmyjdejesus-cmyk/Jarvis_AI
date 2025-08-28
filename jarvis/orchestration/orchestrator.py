from __future__ import annotations

# flake8: noqa

from pathlib import Path
from unittest.mock import MagicMock
import sys
import types
import importlib
import importlib.util
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub optional dependencies
sys.modules.setdefault("neo4j", MagicMock())
keyring_errors = types.ModuleType("keyring.errors")


class NoKeyringError(Exception):
    pass


keyring_errors.NoKeyringError = NoKeyringError
keyring_module = types.ModuleType("keyring")
keyring_module.errors = keyring_errors
sys.modules.setdefault("keyring", keyring_module)
sys.modules.setdefault("keyring.errors", keyring_errors)

langgraph_graph = types.ModuleType("langgraph.graph")
langgraph_graph.END = object()


class StateGraph:  # pragma: no cover - minimal stub
    pass


langgraph_graph.StateGraph = StateGraph
langgraph_module = types.ModuleType("langgraph")
langgraph_module.graph = langgraph_graph
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", langgraph_graph)

# Additional stubs
nx_module = types.ModuleType("networkx")


class DiGraph:  # pragma: no cover - simple stub
    def __init__(self, *a, **k):
        self._nodes = {}
        self._edges = {}

    def add_node(self, node, **k):
        self._nodes[node] = k

    def add_edge(self, u, v, **k):
        self._edges.setdefault(u, [])
        self._edges[u].append((v, k))

    def nodes(self, data=False):
        return self._nodes.items() if data else self._nodes.keys()

    def edges(self, data=False):
        edges = []
        for u, lst in self._edges.items():
            for v, attrs in lst:
                edges.append((u, v, attrs) if data else (u, v))
        return edges

    def predecessors(self, node):
        return [u for u, v in self._edges.items() if v[0][0] == node]

    def successors(self, node):
        return [v[0][0] for v in self._edges.values()]

    def out_degree(self, node):
        return len(self._edges.get(node, []))

    def has_edge(self, u, v):
        return any(edge[0] == v for edge in self._edges.get(u, []))


nx_module.DiGraph = DiGraph
sys.modules.setdefault("networkx", nx_module)


# This is where the old fixture conflicts were. I will add the new combined code
# here to resolve them.
def load_graph_module(monkeypatch):
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

    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.graph", root / "orchestration" / "graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)

    return module


# The mto_cls fixture is a key part of the new testing approach.
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


@pytest.fixture
def graph_module(monkeypatch):
    module = load_graph_module(monkeypatch)
    monkeypatch.setattr(
        module.MultiTeamOrchestrator, "_build_graph", lambda self: DummyGraph()
    )
    return module