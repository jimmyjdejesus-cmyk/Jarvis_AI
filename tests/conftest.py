# flake8: noqa
"""Shared pytest fixtures for the test suite."""
import sys
import types
import enum
from pathlib import Path
from unittest.mock import MagicMock
import importlib.util
from dataclasses import dataclass

import pytest

# Stub external dependencies
neo4j_module = types.ModuleType("neo4j")
neo4j_module.GraphDatabase = object
neo4j_module.Driver = object
sys.modules.setdefault("neo4j", neo4j_module)
neo4j_exceptions = types.ModuleType("neo4j.exceptions")


class ServiceUnavailable(Exception):
    pass


class TransientError(Exception):
    pass


neo4j_exceptions.ServiceUnavailable = ServiceUnavailable
neo4j_exceptions.TransientError = TransientError
sys.modules.setdefault("neo4j.exceptions", neo4j_exceptions)

langgraph_module = types.ModuleType("langgraph")
graph_submodule = types.ModuleType("langgraph.graph")


class StateGraph:
    """Minimal StateGraph stub supporting linear workflows."""

    def __init__(self, _state_type):
        self.nodes = {}
        self.edges: dict[str, list[str]] = {}
        self.entry: str | None = None

    def add_node(self, name: str, func: "Callable"):
        self.nodes[name] = func

    def add_edge(self, src: str, dst: str):
        self.edges.setdefault(src, []).append(dst)

    def set_entry_point(self, name: str):
        self.entry = name

    def compile(self):
        nodes = self.nodes
        edges = self.edges
        entry = self.entry
        end = END

        class Graph:
            def stream(self_inner, state):
                node = entry
                while node is not end:
                    state = nodes[node](state)
                    yield {node: state}
                    next_nodes = edges.get(node, [end])
                    node = next_nodes[0]

        return Graph()


END = object()

graph_submodule.StateGraph = StateGraph
graph_submodule.END = END
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", graph_submodule)

aiohttp_module = types.ModuleType("aiohttp")
sys.modules.setdefault("aiohttp", aiohttp_module)

# Stub optional dependencies
sys.modules.setdefault("neo4j", MagicMock())


class RedisStub:
    """Minimal in-memory stand-in for ``redis.Redis``."""

    def __init__(self, *args, **kwargs) -> None:
        self._store: dict[str, str] = {}
        self._lists: dict[str, list[str]] = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str) -> bool:
        self._store[key] = value
        return True

    def delete(self, *keys: str) -> int:
        removed = 0
        for k in keys:
            if k in self._store:
                del self._store[k]
                removed += 1
        return removed

    def rpush(self, key: str, value: str) -> int:
        lst = self._lists.setdefault(key, [])
        lst.append(value)
        return len(lst)

    def lpop(self, key: str) -> str | None:
        lst = self._lists.get(key)
        if lst:
            return lst.pop(0)
        return None

    def llen(self, key: str) -> int:
        return len(self._lists.get(key, []))

    @classmethod
    def from_url(cls, url: str, *args, **kwargs) -> "RedisStub":  # pragma: no cover - convenience
        return cls()


# Provide minimal redis exception hierarchy used in production code
class RedisError(Exception):
    pass


class ConnectionError(RedisError):
    pass


class TimeoutError(RedisError):
    pass


redis_module = types.ModuleType("redis")
redis_module.Redis = RedisStub
redis_module.RedisError = RedisError
redis_module.ConnectionError = ConnectionError
redis_module.TimeoutError = TimeoutError
sys.modules.setdefault("redis", redis_module)

keyring_module = types.ModuleType("keyring")
keyring_module.get_password = lambda *a, **k: None
sys.modules.setdefault("keyring", keyring_module)
keyring_errors_module = types.ModuleType("keyring.errors")


class NoKeyringError(Exception):
    pass


keyring_errors_module.NoKeyringError = NoKeyringError
sys.modules.setdefault("keyring.errors", keyring_errors_module)

pydantic_module = types.ModuleType("pydantic")


class BaseModel:  # minimal stand-in
    pass


def Field(*args, **kwargs):
    return None


def create_model(name, **fields):
    return type(name, (BaseModel,), fields)


pydantic_module.BaseModel = BaseModel
pydantic_module.Field = Field
pydantic_module.create_model = create_model
sys.modules.setdefault("pydantic", pydantic_module)


# In-memory qdrant_client implementation for tests
class Distance(enum.Enum):
    COSINE = "cosine"


@dataclass
class VectorParams:
    size: int
    distance: Distance


@dataclass
class MatchValue:
    value: str


@dataclass
class FieldCondition:
    key: str
    match: MatchValue


@dataclass
class Filter:
    must: list[FieldCondition]


@dataclass
class PointStruct:
    id: str
    vector: list[float]
    payload: dict


class InMemoryQdrantClient:
    """Minimal in-memory replacement for ``qdrant_client.QdrantClient``."""

    def __init__(self, url: str | None = None) -> None:
        self._collections: dict[str, dict[str, PointStruct]] = {}

    def collection_exists(self, collection_name: str) -> bool:
        return collection_name in self._collections

    def create_collection(
        self, collection_name: str, *, vectors_config: VectorParams
    ) -> None:  # pragma: no cover - trivial
        self._collections.setdefault(collection_name, {})

    def upsert(
        self,
        collection_name: str,
        points: list[PointStruct],
        wait: bool | None = None,
    ) -> None:
        coll = self._collections.setdefault(collection_name, {})
        for p in points:
            coll[p.id] = p

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        query_filter: Filter | None = None,
        limit: int = 10,
    ):
        coll = self._collections.get(collection_name, {})

        def similarity(p: PointStruct) -> float:
            return -sum((a - b) ** 2 for a, b in zip(p.vector, query_vector))

        return sorted(coll.values(), key=similarity, reverse=True)[:limit]

    def scroll(
        self,
        collection_name: str,
        scroll_filter: Filter | None = None,
        with_payload: bool = False,
        limit: int | None = None,
    ):
        coll = self._collections.get(collection_name, {})

        def matches(p: PointStruct) -> bool:
            if scroll_filter is None:
                return True
            return all(
                p.payload.get(cond.key) == cond.match.value
                for cond in scroll_filter.must
            )

        points = [p for p in coll.values() if matches(p)]
        return (points if limit is None else points[:limit], None)

    def delete(
        self,
        collection_name: str,
        *,
        points_selector: list[str] | None = None,
        filter: Filter | None = None,
        wait: bool | None = None,
    ) -> None:
        coll = self._collections.get(collection_name, {})
        if points_selector is not None:
            for pid in points_selector:
                coll.pop(pid, None)
        elif filter is not None:
            to_remove = [
                pid
                for pid, p in coll.items()
                if all(p.payload.get(c.key) == c.match.value for c in filter.must)
            ]
            for pid in to_remove:
                coll.pop(pid, None)


qdrant_client = types.ModuleType("qdrant_client")
qdrant_models = types.ModuleType("qdrant_client.models")
qdrant_client.QdrantClient = InMemoryQdrantClient
qdrant_models.Distance = Distance
qdrant_models.FieldCondition = FieldCondition
qdrant_models.Filter = Filter
qdrant_models.MatchValue = MatchValue
qdrant_models.PointStruct = PointStruct
qdrant_models.VectorParams = VectorParams
qdrant_client.models = qdrant_models
sys.modules.setdefault("qdrant_client", qdrant_client)
sys.modules.setdefault("qdrant_client.models", qdrant_models)

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
    "chromadb.utils.embedding_functions",
    chromadb_embedding,
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

team_agents_module = types.ModuleType("jarvis.orchestration.team_agents")


class OrchestratorAgent:  # pragma: no cover - stub
    pass


class TeamMemberAgent:  # pragma: no cover - stub
    pass


team_agents_module.OrchestratorAgent = OrchestratorAgent
team_agents_module.TeamMemberAgent = TeamMemberAgent
sys.modules.setdefault("jarvis.orchestration.team_agents", team_agents_module)

pruning_module = types.ModuleType("jarvis.orchestration.pruning")


class PruningEvaluator:  # pragma: no cover - stub
    def should_prune(self, team: str) -> bool:
        return False


pruning_module.PruningEvaluator = PruningEvaluator
sys.modules.setdefault("jarvis.orchestration.pruning", pruning_module)

# Additional stubs
requests_module = types.ModuleType("requests")
sys.modules.setdefault("requests", requests_module)
critics_pkg = types.ModuleType("jarvis.agents.critics")
const_module = types.ModuleType("jarvis.agents.critics.constitutional_critic")


class ConstitutionalCritic:
    def __init__(self, *a, **k):
        pass


const_module.ConstitutionalCritic = ConstitutionalCritic
critics_pkg.constitutional_critic = const_module
sys.modules.setdefault("jarvis.agents.critics", critics_pkg)
sys.modules.setdefault(
    "jarvis.agents.critics.constitutional_critic",
    const_module,
)

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


class _DummyVectorStore:
    """Minimal in-memory vector store for tests."""

    def __init__(self) -> None:
        self._docs: list[str] = []

    def add_text(
        self,
        principal: str,
        scope: str,
        key: str,
        text: str,
    ) -> None:
        self._docs.append(text)

    def query_text(self, query: str, n_results: int = 1):
        if self._docs:
            return {"documents": [[self._docs[-1]]]}
        return {"documents": [[]]}

    def evict_scope(self, principal: str, scope: str) -> None:
        self._docs.clear()


memory_service.Metrics = Metrics
memory_service.NegativeCheck = NegativeCheck
memory_service.Outcome = Outcome
memory_service.PathRecord = PathRecord
memory_service.PathSignature = PathSignature
memory_service.avoid_negative = avoid_negative
memory_service.record_path = record_path
memory_service.vector_store = _DummyVectorStore()
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

# Ensure repository root on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Lightweight workflows package to avoid circular imports
spec = importlib.util.spec_from_file_location(
    "jarvis.workflows.engine",
    ROOT / "jarvis/workflows/engine.py",
)
engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)
workflows_pkg = types.ModuleType("jarvis.workflows")
workflows_pkg.engine = engine_module
sys.modules.setdefault("jarvis.workflows", workflows_pkg)
sys.modules.setdefault("jarvis.workflows.engine", engine_module)


@pytest.fixture
def mock_neo4j_graph(monkeypatch):
    """Provide a mock Neo4j graph for tests."""

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
    yield mock_graph


class AIAgent:
    """Minimal base agent stub used for tests."""


class ExecutiveAgent(AIAgent):
    """Stub executive agent to satisfy imports during testing."""


eco_pkg = types.ModuleType("jarvis.ecosystem")
meta_module = types.ModuleType("jarvis.ecosystem.meta_intelligence")
meta_module.AIAgent = AIAgent
meta_module.ExecutiveAgent = ExecutiveAgent
eco_pkg.ExecutiveAgent = ExecutiveAgent
eco_pkg.meta_intelligence = meta_module
sys.modules.setdefault("jarvis.ecosystem", eco_pkg)
sys.modules.setdefault("jarvis.ecosystem.meta_intelligence", meta_module)


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
            pass