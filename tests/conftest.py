"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import sys
import types
import importlib.util
import enum
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock
import pytest
import builtins
import logging as _logging

# flake8: noqa

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
keyring_module.get_password = lambda *args, **kwargs: None
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
        self._edges.setdefault(u, []).append((v, k))

    def nodes(self, data=False):
        return self._nodes.items() if data else self._nodes.keys()

    def edges(self, data=False):
        edges = []
        for u, lst in self._edges.items():
            edges.extend([(u, v, attrs) if data else (u, v) for v, attrs in lst])
        return edges

    def predecessors(self, node):
        return [u for u, v in self._edges.items() if v[0][0] == node]

    def successors(self, node):
        return [t for t, attrs in self._edges.get(node, [])]

    def has_node(self, node):
        return node in self._nodes

    def has_edge(self, u, v):
        lst = self._edges.get(u, [])
        return v in [t for t, attrs in lst]

    def in_edges(self, node, data=False):
        edges = []
        for u, lst in self._edges.items():
            for v, attrs in lst:
                if v == node:
                    edges.append((u, v, attrs) if data else (u, v))
        return edges

    def out_edges(self, node, data=False):
        lst = self._edges.get(node, [])
        return [(node, t, attrs) if data else (node, t) for t, attrs in lst]


nx_module.DiGraph = DiGraph
sys.modules.setdefault("networkx", nx_module)

requests_module = types.ModuleType('requests')
sys.modules.setdefault('requests', requests_module)
critics_pkg = types.ModuleType('jarvis.agents.critics')
const_module = types.ModuleType('jarvis.agents.critics.constitutional_critic')


class ConstitutionalCritic:
    def __init__(self, *a, **k):
        pass


const_module.ConstitutionalCritic = ConstitutionalCritic
critics_pkg.constitutional_critic = const_module
sys.modules.setdefault('jarvis.agents.critics', critics_pkg)
sys.modules.setdefault('jarvis.agents.critics.constitutional_critic', const_module)


# Internal package stubs
homeostasis_module = types.ModuleType("jarvis.homeostasis")
monitor_submodule = types.ModuleType("jarvis.homeostasis.monitor")


class SystemMonitor:
    pass


monitor_submodule.SystemMonitor = SystemMonitor
sys.modules.setdefault("jarvis.homeostasis", homeostasis_module)
sys.modules.setdefault("jarvis.homeostasis.monitor", monitor_submodule)

memory_service = types.ModuleType("memory_service")
models_sub = types.ModuleType("memory_service.models")


class Metrics:
    def __init__(self, novelty=0.0, growth=0.0, cost=0.0):
        self.novelty = novelty
        self.growth = growth
        self.cost = cost


class NegativeCheck:  # pragma: no cover - stub
    def __init__(self, *a, **k):
        pass


class Outcome:
    def __init__(self, result="", oracle_score=0.0):
        self.result = result
        self.oracle_score = oracle_score


class PathRecord:
    def __init__(self, *a, **k):
        pass


class PathSignature:
    def __init__(self, *a, **k):
        pass


def avoid_negative(*a, **k):
    return {"avoid": False, "results": []}


def record_path(*a, **k):
    return None


memory_service.Metrics = Metrics
memory_service.NegativeCheck = NegativeCheck
memory_service.Outcome = Outcome
memory_service.PathRecord = PathRecord
memory_service.PathSignature = PathSignature
memory_service.avoid_negative = avoid_negative
memory_service.record_path = record_path
memory_service.vector_store = None
sys.modules.setdefault("memory_service", memory_service)
sys.modules.setdefault("memory_service.models", models_sub)

# Stub jarvis.ecosystem to prevent circular imports during test bootstrap
ecosystem_pkg = types.ModuleType("jarvis.ecosystem")
meta_module = types.ModuleType("jarvis.ecosystem.meta_intelligence")


class ExecutiveAgent:  # pragma: no cover - minimal placeholder
    pass


meta_module.ExecutiveAgent = ExecutiveAgent
ecosystem_pkg.meta_intelligence = meta_module
ecosystem_pkg.superintelligence = types.ModuleType(
    "jarvis.ecosystem.superintelligence"
)
sys.modules.setdefault("jarvis.ecosystem", ecosystem_pkg)
sys.modules.setdefault("jarvis.ecosystem.meta_intelligence", meta_module)
sys.modules.setdefault(
    "jarvis.ecosystem.superintelligence", ecosystem_pkg.superintelligence
)

# Simplified team agent to satisfy orchestration imports
team_agents_module = types.ModuleType("jarvis.orchestration.team_agents")


class BlackInnovatorAgent:  # pragma: no cover - minimal placeholder
    pass


team_agents_module.BlackInnovatorAgent = BlackInnovatorAgent
sys.modules.setdefault("jarvis.orchestration.team_agents", team_agents_module)


# Lightweight workflows package to avoid circular imports
spec = importlib.util.spec_from_file_location(
    "jarvis.workflows.engine", ROOT / "jarvis/workflows/engine.py"
)
engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)
workflows_pkg = types.ModuleType("jarvis.workflows")
workflows_pkg.engine = engine_module
sys.modules.setdefault("jarvis.workflows", workflows_pkg)
sys.modules.setdefault("jarvis.workflows.engine", engine_module)


@pytest.fixture(autouse=True)
def stub_keyring(monkeypatch):
    """Avoid accessing system keyring during tests."""
    storage = {}

    def _get_password(service, username):
        return storage.get((service, username))

    def _set_password(service, username, password):
        storage[(service, username)] = password

    monkeypatch.setattr(keyring, "get_password", _get_password)
    monkeypatch.setattr(keyring, "set_password", _set_password)


@pytest.fixture
def mock_neo4j_graph(monkeypatch):
    """Provide a mock Neo4j graph for tests requiring persistence."""
    mock_graph = MagicMock()
    mock_graph.connect = MagicMock()
    mock_graph.close = MagicMock()
    mock_graph.run = MagicMock(
        return_value=MagicMock(data=MagicMock(return_value=[]))
    )
    monkeypatch.setattr(
        "jarvis.world_model.neo4j_graph.Neo4jGraph",
        MagicMock(return_value=mock_graph),
    )
    return mock_graph