"""Shared pytest fixtures for the test suite."""

import sys
import types
from pathlib import Path
from enum import Enum
from unittest.mock import MagicMock, Mock
import pytest

# Stub external dependencies
neo4j_module = types.ModuleType("neo4j")
neo4j_module.Driver = object


class GraphDatabase:
    @staticmethod
    def driver(uri, auth=None):
        return object()


neo4j_module.GraphDatabase = GraphDatabase
exceptions_submodule = types.ModuleType("neo4j.exceptions")


class ServiceUnavailable(Exception):
    pass


class TransientError(Exception):
    pass


exceptions_submodule.ServiceUnavailable = ServiceUnavailable
exceptions_submodule.TransientError = TransientError
neo4j_module.exceptions = exceptions_submodule
sys.modules.setdefault("neo4j", neo4j_module)
sys.modules.setdefault("neo4j.exceptions", exceptions_submodule)

langgraph_module = types.ModuleType("langgraph")
graph_submodule = types.ModuleType("langgraph.graph")
graph_submodule.StateGraph = object
graph_submodule.END = None
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", graph_submodule)

aiohttp_module = types.ModuleType("aiohttp")
web_submodule = types.ModuleType("aiohttp.web")


class Application:  # pragma: no cover - simple stub
    pass


class Response:  # pragma: no cover - simple stub
    pass


web_submodule.Application = Application
web_submodule.Response = Response
aiohttp_module.web = web_submodule
sys.modules.setdefault("aiohttp", aiohttp_module)
sys.modules.setdefault("aiohttp.web", web_submodule)

keyring_module = types.ModuleType("keyring")
keyring_module.get_password = lambda *a, **k: None
sys.modules.setdefault("keyring", keyring_module)
keyring_errors_module = types.ModuleType("keyring.errors")


class NoKeyringError(Exception):
    pass


keyring_errors_module.NoKeyringError = NoKeyringError
sys.modules.setdefault("keyring.errors", keyring_errors_module)

try:
    import pydantic  # type: ignore
except Exception:
    # Minimal fallback when pydantic is not available in the test
    # environment (keeps tests fast and avoids hard dependency in some dev setups).
    pydantic_module = types.ModuleType("pydantic")


    class BaseModel:  # minimal stand-in
        pass


    def Field(*args, **kwargs):
        return None


    pydantic_module.BaseModel = BaseModel
    pydantic_module.Field = Field


    def create_model(name, **fields):
        return type(name, (BaseModel,), fields)


    pydantic_module.create_model = create_model
    sys.modules.setdefault("pydantic", pydantic_module)

    # Minimal config loader shim for legacy imports (e.g. config.config_loader.load_config)
    config_module = types.ModuleType("config")
    config_loader_module = types.ModuleType("config.config_loader")

    def load_config(explicit_path: str | None = None):  # pragma: no cover - test shim
        return {}

    config_loader_module.load_config = load_config
    config_module.config_loader = config_loader_module
    sys.modules.setdefault("config", config_module)
    sys.modules.setdefault("config.config_loader", config_loader_module)

chromadb_module = types.ModuleType("chromadb")
chromadb_utils = types.ModuleType("chromadb.utils")
chromadb_embedding = types.ModuleType("chromadb.utils.embedding_functions")


class EmbeddingFunction:
    pass


chromadb_embedding.EmbeddingFunction = EmbeddingFunction
chromadb_utils.embedding_functions = chromadb_embedding
sys.modules.setdefault("chromadb", chromadb_module)
sys.modules.setdefault("chromadb.utils", chromadb_utils)
sys.modules.setdefault(
    "chromadb.utils.embedding_functions", chromadb_embedding
)

nx_module = types.ModuleType("networkx")


class DiGraph:
    def __init__(self):
        self._nodes = {}
        self._edges = {}

    def add_node(self, node, **attrs):
        self._nodes[node] = attrs

    def add_edge(self, s, t, **attrs):
        self._edges.setdefault(s, []).append((t, attrs))

    def nodes(self, data=False):
        return list(self._nodes.items()) if data else list(self._nodes.keys())

    def edges(self, data=False):
        edges = []
        for s, lst in self._edges.items():
            for t, attrs in lst:
                edges.append((s, t, attrs) if data else (s, t))
        return edges

    def out_edges(self, node, data=False):
        lst = self._edges.get(node, [])
        return [(node, t, attrs) if data else (node, t) for t, attrs in lst]


nx_module.DiGraph = DiGraph
sys.modules.setdefault("networkx", nx_module)

# Additional stubs
requests_module = types.ModuleType("requests")

def mock_response():
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = {
        "total_events": 0,
        "ingested": True,
        "job_id": "test-job",
        "status": "completed"
    }
    resp.text = ""
    return resp

requests_module.get = lambda *a, **k: mock_response()
requests_module.post = lambda *a, **k: mock_response()
sys.modules.setdefault("requests", requests_module)
critics_pkg = types.ModuleType("jarvis.agents.critics")
const_module = types.ModuleType("jarvis.agents.critics.constitutional_critic")


class ConstitutionalCritic:
    def __init__(self, *a, **k):
        pass

    async def review(self, *args, **kwargs):
        return {"approved": True, "feedback": ""}


const_module.ConstitutionalCritic = ConstitutionalCritic
critics_pkg.constitutional_critic = const_module
sys.modules.setdefault("jarvis.agents.critics", critics_pkg)
sys.modules.setdefault(
    "jarvis.agents.critics.constitutional_critic", const_module
)

# Minimal specialist registry for orchestrator imports
specialist_registry_module = types.ModuleType(
    "jarvis.agents.specialist_registry"
)


def get_specialist_registry():  # pragma: no cover - simple stub
    return {}


specialist_registry_module.get_specialist_registry = get_specialist_registry
sys.modules.setdefault(
    "jarvis.agents.specialist_registry", specialist_registry_module
)
# Close the setdefault call above.

# Minimal factory shim for tests: provide create_specialist so imports
# that expect it (e.g., orchestrator) do not fail during collection.
def create_specialist(name, *args, **kwargs):  # pragma: no cover - test shim
    return MagicMock(name=f"specialist:{name}")

specialist_registry_module.create_specialist = create_specialist


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
memory_service.__path__ = []
hypergraph_sub = types.ModuleType("memory_service.hypergraph")
vector_store_sub = types.ModuleType("memory_service.vector_store")


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


class Hypergraph:  # pragma: no cover - stub
    pass


class VectorStore:  # pragma: no cover - stub
    pass


hypergraph_sub.Hypergraph = Hypergraph
vector_store_sub.VectorStore = VectorStore
memory_service.hypergraph = hypergraph_sub
memory_service.vector_store = vector_store_sub
sys.modules.setdefault("memory_service", memory_service)
sys.modules.setdefault("memory_service.models", models_sub)
sys.modules.setdefault("memory_service.hypergraph", hypergraph_sub)
sys.modules.setdefault("memory_service.vector_store", vector_store_sub)

# Stub jarvis.ecosystem to prevent circular imports during test bootstrap
ecosystem_pkg = types.ModuleType("jarvis.ecosystem")
meta_module = types.ModuleType("jarvis.ecosystem.meta_intelligence")


class ExecutiveAgent:  # pragma: no cover - minimal placeholder
    pass


meta_module.ExecutiveAgent = ExecutiveAgent
ecosystem_pkg.meta_intelligence = meta_module
ecosystem_pkg.ExecutiveAgent = ExecutiveAgent
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

# MCP client stub to satisfy CLI imports
mcp_client_module = types.ModuleType("jarvis.mcp.client")


class MCPClient:  # pragma: no cover - stub
    pass


class ModelRouter:  # pragma: no cover - stub
    pass


class MCPServerManager:  # pragma: no cover - stub
    pass


mcp_client_module.MCPClient = MCPClient
mcp_client_module.ModelRouter = ModelRouter
mcp_client_module.MCPServerManager = MCPServerManager
sys.modules.setdefault("jarvis.mcp.client", mcp_client_module)

# jarvis.mcp module
mcp_module = types.ModuleType("jarvis.mcp")
mcp_module.MCPClient = MCPClient
mcp_module.ModelRouter = ModelRouter
mcp_module.MCPServerManager = MCPServerManager
sys.modules.setdefault("jarvis.mcp", mcp_module)

# Ensure repository root on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Lightweight workflows package to avoid heavy dependencies
workflows_pkg = types.ModuleType("jarvis.workflows")
engine_module = types.ModuleType("jarvis.workflows.engine")


class WorkflowStatus(Enum):  # pragma: no cover - minimal enum
    PENDING = "pending"


class WorkflowEngine:  # pragma: no cover - stub
    pass


def from_mission_dag(*args, **kwargs):  # pragma: no cover - stub
    return None


engine_module.WorkflowStatus = WorkflowStatus
engine_module.WorkflowEngine = WorkflowEngine
engine_module.from_mission_dag = from_mission_dag
engine_module.workflow_engine = object()
workflows_pkg.engine = engine_module
sys.modules.setdefault("jarvis.workflows", workflows_pkg)
sys.modules.setdefault("jarvis.workflows.engine", engine_module)


@pytest.fixture
def client():
    """Mock HTTP client for API tests"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": "test response", "id": "test-id", "object": "chat.completion"}
    mock_client.post.return_value = mock_response
    return mock_client
