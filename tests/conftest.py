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

# Stub chromadb embedding functions to satisfy project_memory imports
chromadb = types.ModuleType("chromadb")
chromadb.PersistentClient = MagicMock()
chromadb_utils = types.ModuleType("chromadb.utils")
chromadb_embed = types.ModuleType("chromadb.utils.embedding_functions")

class _EmbeddingFunction:
    pass

chromadb_embed.EmbeddingFunction = _EmbeddingFunction
chromadb_utils.embedding_functions = chromadb_embed
sys.modules.setdefault("chromadb", chromadb)
sys.modules.setdefault("chromadb.utils", chromadb_utils)
sys.modules.setdefault("chromadb.utils.embedding_functions", chromadb_embed)

# Stub modules referenced by orchestration and MCP components
sys.modules.setdefault("jarvis.monitoring.performance", MagicMock())
sys.modules.setdefault("aiohttp", MagicMock())

# Load orchestration submodules without executing their heavy package __init__
orchestration_pkg = types.ModuleType("jarvis.orchestration")
orchestration_pkg.__path__ = [str(ROOT / "jarvis" / "orchestration")]
sys.modules.setdefault("jarvis.orchestration", orchestration_pkg)

# Minimal Mission model and persistence helpers
mission_module = types.ModuleType("jarvis.orchestration.mission")

@dataclass
class Mission:  # pragma: no cover - simple stub
    id: str
    title: str
    goal: str
    inputs: dict
    risk_level: str
    dag: object

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "goal": self.goal,
            "inputs": self.inputs,
            "risk_level": self.risk_level,
            "dag": {},
        }

def save_mission(mission: Mission) -> None:  # pragma: no cover - stub
    pass

def load_mission(mission_id: str) -> Mission:  # pragma: no cover - stub
    raise FileNotFoundError

mission_module.Mission = Mission
mission_module.save_mission = save_mission
mission_module.load_mission = load_mission
@dataclass
class MissionDAG:  # pragma: no cover - simple stub
    mission_id: str
    nodes: dict
    edges: list | None = None
    rationale: str = ""

    def to_dict(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "nodes": self.nodes,
            "edges": self.edges or [],
            "rationale": self.rationale,
        }

mission_module.MissionDAG = MissionDAG

@dataclass
class MissionNode:  # pragma: no cover - simple stub
    step_id: str
    capability: str
    team_scope: str
    details: str | None = None
    hitl_gate: bool = False
    deps: list | None = None
    state: MissionNodeState | None = None


@dataclass
class MissionNodeState:  # pragma: no cover - simple stub
    status: str = "pending"
    started_at: float | None = None
    completed_at: float | None = None
    provenance: dict | None = None

mission_module.MissionNode = MissionNode
mission_module.MissionNodeState = MissionNodeState
sys.modules.setdefault("jarvis.orchestration.mission", mission_module)

# Load real mission_planner implementation
spec = importlib.util.spec_from_file_location(
    "jarvis.orchestration.mission_planner", ROOT / "jarvis" / "orchestration" / "mission_planner.py"
)
mission_planner_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mission_planner_module)
sys.modules["jarvis.orchestration.mission_planner"] = mission_planner_module

# Minimal workflow engine stub with WorkflowStatus enum
workflow_engine = types.ModuleType("jarvis.workflows.engine")
class _WorkflowStatus(enum.Enum):
    PENDING = "PENDING"
workflow_engine.WorkflowStatus = _WorkflowStatus
sys.modules.setdefault("jarvis.workflows.engine", workflow_engine)

# Provide a default model_client for agent mission planner patching
import jarvis.agents.mission_planner as _agent_mp
_agent_mp.model_client = MagicMock()

# In-memory task queue to replace RedisTaskQueue
task_queue_module = types.ModuleType("jarvis.orchestration.task_queue")

class RedisTaskQueue:  # pragma: no cover - simple stub
    def __init__(self, name: str = "tasks") -> None:
        self.name = name
        self.tasks: list = []

    def enqueue(self, task: dict) -> None:
        self.tasks.append(task)

task_queue_module.RedisTaskQueue = RedisTaskQueue
sys.modules.setdefault("jarvis.orchestration.task_queue", task_queue_module)
mission_planner_module.RedisTaskQueue = RedisTaskQueue


@pytest.fixture
def mock_neo4j_graph(monkeypatch):
    """Provide a mock Neo4j graph for tests."""

    mock_graph = MagicMock()
    monkeypatch.setattr(
        "jarvis.world_model.neo4j_graph.Neo4jGraph",
        MagicMock(return_value=mock_graph),
    )
    return mock_graph
