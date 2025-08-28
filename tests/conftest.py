from __future__ import annotations

# flake8: noqa
from pathlib import Path
from unittest.mock import MagicMock
import sys
import types
import importlib.util
import enum
from dataclasses import dataclass
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
# Minimal qdrant_client stub so imports succeed without the heavy dependency
qdrant_client = types.ModuleType("qdrant_client")
qdrant_client.QdrantClient = MagicMock()
qdrant_models = types.ModuleType("qdrant_client.models")
qdrant_client.models = qdrant_models
sys.modules.setdefault("qdrant_client", qdrant_client)
sys.modules.setdefault("qdrant_client.models", qdrant_models)
for name in [
    "Distance",
    "FieldCondition",
    "Filter",
    "MatchValue",
    "PointStruct",
    "VectorParams",
]:
    setattr(qdrant_models, name, MagicMock())


def load_graph_module(monkeypatch):
    """Load `jarvis.orchestration.graph` with isolated stubs."""
    root = Path(__file__).resolve().parents[1] / "jarvis"

    # Provide fresh langgraph/networkx stubs per invocation
    langgraph_graph = types.ModuleType("langgraph.graph")
    langgraph_graph.END = object()

    class StateGraph:  # pragma: no cover - minimal stub
        def __init__(self, *args, **kwargs):
            self.nodes = {}
            self.edges = {}
            self.entry = None

        def add_node(self, name, fn):
            self.nodes[name] = fn

        def set_entry_point(self, name):
            self.entry = name

        def add_edge(self, src, dst):
            self.edges[src] = dst

        def compile(self):
            nodes = self.nodes
            edges = self.edges
            entry = self.entry

            class _CompiledGraph:
                def stream(self, state):
                    current = entry
                    while current:
                        fn = nodes[current]
                        state = fn(state)
                        yield {current: state}
                        if state.get("halt"):
                            break
                        nxt = edges.get(current)
                        if nxt is langgraph_graph.END:
                            break
                        current = nxt

            return _CompiledGraph()

    langgraph_graph.StateGraph = StateGraph
    langgraph_module = types.ModuleType("langgraph")
    langgraph_module.graph = langgraph_graph
    monkeypatch.setitem(sys.modules, "langgraph", langgraph_module)
    monkeypatch.setitem(sys.modules, "langgraph.graph", langgraph_graph)
    monkeypatch.setitem(sys.modules, "networkx", types.ModuleType("networkx"))

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
    monkeypatch.setitem(sys.modules, "jarvis.orchestration.pruning", pruning_stub)

    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.graph", root / "orchestration" / "graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module
