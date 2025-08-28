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