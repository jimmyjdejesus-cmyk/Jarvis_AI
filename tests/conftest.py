"""Test configuration and dependency stubs for unit tests."""

import sys
import types
from pathlib import Path
JARVIS_PATH = Path(__file__).resolve().parent.parent / "jarvis"
jarvis_pkg = types.ModuleType("jarvis")
critics_pkg = types.ModuleType("jarvis.agents.critics")
constitutional_critic = types.ModuleType("jarvis.agents.critics.constitutional_critic")
class ConstitutionalCritic:  # pragma: no cover - stub
    def __init__(self, *args, **kwargs):
        pass
constitutional_critic.ConstitutionalCritic = ConstitutionalCritic
sys.modules.setdefault("jarvis.agents.critics", critics_pkg)
sys.modules.setdefault("jarvis.agents.critics.constitutional_critic", constitutional_critic)

orch_pkg = types.ModuleType("jarvis.orchestration")
orch_pkg.__path__ = [str(JARVIS_PATH / "orchestration")]
sys.modules.setdefault("jarvis.orchestration", orch_pkg)

jarvis_pkg.__path__ = [str(JARVIS_PATH)]
sys.modules.setdefault("jarvis", jarvis_pkg)


# Provide lightweight stand-ins for optional external dependencies
chromadb = types.ModuleType('chromadb')
chromadb.utils = types.ModuleType('utils')
memory_service = types.ModuleType("memory_service")
class PathRecord:
    pass
class PathSignature:
    pass
class Outcome:
    pass
class Metrics:
    pass
class NegativeCheck:
    pass
def record_path(*args, **kwargs):
    return None
def avoid_negative(*args, **kwargs):
    return False
memory_service.record_path = record_path
memory_service.avoid_negative = avoid_negative
memory_service.PathRecord = PathRecord
memory_service.PathSignature = PathSignature
memory_service.Outcome = Outcome
memory_service.Metrics = Metrics
memory_service.NegativeCheck = NegativeCheck
class _VectorStore:
    def add_text(self, *args, **kwargs):
        return None
    def query_text(self, query, n_results=1):
        return {"documents": [[]]}
memory_service.vector_store = _VectorStore()

sys.modules.setdefault("memory_service", memory_service)

pydantic = types.ModuleType("pydantic")
class BaseModel:  # pragma: no cover - stub
    pass
def Field(default=None, *args, **kwargs):  # pragma: no cover - stub
    return default
pydantic.BaseModel = BaseModel
pydantic.Field = Field
sys.modules.setdefault("pydantic", pydantic)

langgraph = types.ModuleType("langgraph")
langgraph.graph = types.ModuleType("graph")
langgraph.graph.END = object()
class StateGraph:  # pragma: no cover - stub
    pass
langgraph.graph.StateGraph = StateGraph
sys.modules.setdefault("langgraph", langgraph)
sys.modules.setdefault("langgraph.graph", langgraph.graph)

chromadb.utils.embedding_functions = types.ModuleType('embedding_functions')

class EmbeddingFunction:  # pragma: no cover - simple stub
    """Minimal base embedding function stub."""

class HashEmbeddingFunction(EmbeddingFunction):  # pragma: no cover - simple stub
    """Hash-based embedding function stub."""

chromadb.utils.embedding_functions.EmbeddingFunction = EmbeddingFunction
chromadb.utils.embedding_functions.HashEmbeddingFunction = HashEmbeddingFunction
sys.modules.setdefault('chromadb', chromadb)
sys.modules.setdefault('chromadb.utils', chromadb.utils)
sys.modules.setdefault('chromadb.utils.embedding_functions', chromadb.utils.embedding_functions)

neo4j_module = types.ModuleType('neo4j')

class GraphDatabase:  # pragma: no cover - simple stub
    """Stub GraphDatabase with no-op driver."""
    @staticmethod
    def driver(*args, **kwargs):
        return None

neo4j_module.GraphDatabase = GraphDatabase
neo4j_module.Driver = object  # type: ignore[attr-defined]
sys.modules.setdefault('neo4j', neo4j_module)

specialist_registry = types.ModuleType('jarvis.agents.specialist_registry')
specialist_registry.get_specialist_registry = lambda: []  # pragma: no cover - stub
specialist_registry.create_specialist = (
    lambda name, mcp_client, knowledge_graph=None: None
)  # pragma: no cover - stub
sys.modules.setdefault('jarvis.agents.specialist_registry', specialist_registry)

# Ensure standard library modules required by tests are present
sys.modules.setdefault('psutil', types.ModuleType('psutil'))
sys.modules.setdefault('networkx', types.ModuleType('networkx'))

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
