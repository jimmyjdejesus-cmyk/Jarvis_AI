"""Shared pytest fixtures for the test suite."""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock
import importlib.util

import pytest

# Stub external dependencies
neo4j_module = types.ModuleType("neo4j")
neo4j_module.GraphDatabase = object
neo4j_module.Driver = object
sys.modules.setdefault("neo4j", neo4j_module)

langgraph_module = types.ModuleType("langgraph")
graph_submodule = types.ModuleType("langgraph.graph")
graph_submodule.StateGraph = object
graph_submodule.END = None
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", graph_submodule)

aiohttp_module = types.ModuleType("aiohttp")
sys.modules.setdefault("aiohttp", aiohttp_module)

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


pydantic_module.BaseModel = BaseModel
pydantic_module.Field = Field
sys.modules.setdefault("pydantic", pydantic_module)

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


@pytest.fixture
def mock_neo4j_graph(monkeypatch):
    """Provide a mock Neo4j graph for tests requiring persistence."""
    mock_graph = MagicMock()
    mock_graph.connect = MagicMock()
    mock_graph.close = MagicMock()
    mock_graph.run = MagicMock(
        return_value=MagicMock(data=MagicMock(return_value=[])),
    )
    monkeypatch.setattr(
        "jarvis.world_model.neo4j_graph.Neo4jGraph",
        MagicMock(return_value=mock_graph),
    )
    return mock_graph


@pytest.fixture
def multi_team_orchestrator_cls():
    """Construct a `MultiTeamOrchestrator` wired to in-memory stubs.

    The returned class uses `_DummyVectorStore` and lightweight module
    replacements so orchestration tests can run without external services.
    """

    root = Path(__file__).resolve().parents[1] / "jarvis"

    jarvis_stub = types.ModuleType("jarvis")
    jarvis_stub.__path__ = [str(root)]
    sys.modules.setdefault("jarvis", jarvis_stub)

    orch_stub = types.ModuleType("jarvis.orchestration")
    orch_stub.__path__ = [str(root / "orchestration")]
    sys.modules.setdefault("jarvis.orchestration", orch_stub)

    team_agents_stub = types.ModuleType(
        "jarvis.orchestration.team_agents",
    )

    class TeamMemberAgent:
        """Stub team member agent."""

        pass

    class OrchestratorAgent:
        """Stub orchestrator agent."""

        pass

    team_agents_stub.TeamMemberAgent = TeamMemberAgent
    team_agents_stub.OrchestratorAgent = OrchestratorAgent
    sys.modules.setdefault(
        "jarvis.orchestration.team_agents",
        team_agents_stub,
    )

    pruning_stub = types.ModuleType("jarvis.orchestration.pruning")

    class PruningEvaluator:
        def should_prune(self, team):  # pragma: no cover - simple stub
            return False

        async def evaluate(self, team, output):
            """Simple stub evaluation."""
            return None  # pragma: no cover

    pruning_stub.PruningEvaluator = PruningEvaluator
    sys.modules.setdefault("jarvis.orchestration.pruning", pruning_stub)

    spec = importlib.util.spec_from_file_location(
        "jarvis.orchestration.graph", root / "orchestration" / "graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

    def dummy_build_graph(self):
        class DummyGraph:
            def invoke(_, state):
                state = self._run_competitive_pair(state)
                state = self._run_adversary_pair(state)
                state = self._run_innovators_disruptors(state)
                state = self._broadcast_findings(state)
                state = self._run_security_quality(state)
                return state

            def stream(_, state):
                for func, name in [
                    (self._run_competitive_pair, "competitive_pair"),
                    (self._run_adversary_pair, "adversary_pair"),
                    (self._run_innovators_disruptors, "innovators_disruptors"),
                    (self._broadcast_findings, "broadcast_findings"),
                    (self._run_security_quality, "security_quality"),
                ]:
                    state = func(state)
                    yield {name: state}

        return DummyGraph()

    module.MultiTeamOrchestrator._build_graph = dummy_build_graph
    return module.MultiTeamOrchestrator
