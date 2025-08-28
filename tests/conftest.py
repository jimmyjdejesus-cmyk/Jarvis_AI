"""Shared pytest fixtures for the test suite."""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock
import importlib.util

import pytest
import keyring
import builtins
import logging as _logging

builtins.Path = Path
builtins.sys = sys
builtins.logging = _logging

# Provide a minimal langgraph stub if the package is unavailable
try:  # pragma: no cover - optional dependency
    import langgraph  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    langgraph = types.ModuleType("langgraph")
    graph_mod = types.ModuleType("langgraph.graph")
    graph_mod.StateGraph = object
    graph_mod.END = None
    sys.modules["langgraph"] = langgraph
    sys.modules["langgraph.graph"] = graph_mod

# Minimal memory_service stub to avoid external services
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

# Minimal ProjectMemory stub to avoid chromadb dependency
project_memory = types.ModuleType("jarvis.memory.project_memory")


class ProjectMemory:
    def add(self, *a, **k):  # pragma: no cover - stub
        pass

    def query(self, *a, **k):  # pragma: no cover - stub
        return []


project_memory.ProjectMemory = ProjectMemory
sys.modules.setdefault("jarvis.memory.project_memory", project_memory)

# Stub neo4j module to avoid optional dependency
neo4j_stub = types.ModuleType("neo4j")
neo4j_stub.GraphDatabase = object
neo4j_stub.Driver = object
sys.modules.setdefault("neo4j", neo4j_stub)

neo4j_exceptions = types.ModuleType("neo4j.exceptions")


class ServiceUnavailable(Exception):  # pragma: no cover - stub
    pass


class TransientError(Exception):  # pragma: no cover - stub
    pass


neo4j_exceptions.ServiceUnavailable = ServiceUnavailable
neo4j_exceptions.TransientError = TransientError
neo4j_stub.exceptions = neo4j_exceptions
sys.modules.setdefault("neo4j.exceptions", neo4j_exceptions)

# Ensure repository root on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
