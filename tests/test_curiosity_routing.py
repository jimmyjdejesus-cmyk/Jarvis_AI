import sys
import types
import asyncio

# Stub optional heavy dependencies before importing the package
langgraph = types.ModuleType("langgraph")
langgraph_graph = types.ModuleType("langgraph.graph")
langgraph_graph.END = object()


class _StateGraph:  # minimal placeholder
    pass


langgraph_graph.StateGraph = _StateGraph
sys.modules["langgraph"] = langgraph
sys.modules["langgraph.graph"] = langgraph_graph

# Stub memory_service used by orchestrator
memory_service = types.ModuleType("memory_service")


class _Dummy:
    def __init__(self, **kwargs):
        pass


def _avoid_negative(_):
    return {"avoid": False, "results": []}


def _record_path(_):
    return None


memory_service.Metrics = _Dummy
memory_service.NegativeCheck = _Dummy
memory_service.Outcome = _Dummy
memory_service.PathRecord = _Dummy
memory_service.PathSignature = _Dummy
memory_service.avoid_negative = _avoid_negative
memory_service.record_path = _record_path
memory_service.vector_store = object()
sys.modules["memory_service"] = memory_service

# Stub project memory to avoid chromadb dependency
jarvis_memory = types.ModuleType("jarvis.memory")
jarvis_memory.__path__ = []  # mark as package
project_memory = types.ModuleType("jarvis.memory.project_memory")


class _MemoryManager:
    pass


class _ProjectMemory(_MemoryManager):
    def __init__(self, *args, **kwargs):
        pass


project_memory.MemoryManager = _MemoryManager
project_memory.ProjectMemory = _ProjectMemory
sys.modules["jarvis.memory"] = jarvis_memory
sys.modules["jarvis.memory.project_memory"] = project_memory

# Stub neo4j dependency used by world_model
neo4j = types.ModuleType("neo4j")


class _GraphDatabase:
    @staticmethod
    def driver(*args, **kwargs):  # pragma: no cover - stub
        return None


neo4j.GraphDatabase = _GraphDatabase
neo4j.Driver = object
sys.modules["neo4j"] = neo4j

# Stub networkx used by knowledge graph
networkx = types.ModuleType("networkx")


class _DiGraph:
    def __init__(self, *args, **kwargs):  # pragma: no cover - stub
        pass

    def add_node(self, *args, **kwargs):  # pragma: no cover - stub
        pass

    def add_edge(self, *args, **kwargs):  # pragma: no cover - stub
        pass

    def nodes(self, data=False):  # pragma: no cover - stub
        return []

    def edges(self, data=False):  # pragma: no cover - stub
        return []

    def out_edges(self, *args, **kwargs):  # pragma: no cover - stub
        return []


networkx.DiGraph = _DiGraph
sys.modules["networkx"] = networkx

from jarvis.agents.curiosity_router import CuriosityRouter  # noqa: E402
from jarvis.ecosystem.meta_intelligence import ExecutiveAgent  # noqa: E402


def test_curiosity_router_converts_question():
    router = CuriosityRouter()
    directive = router.route("What is the capital of France?")
    assert directive == "Investigate: What is the capital of France"


def test_curiosity_router_sanitizes_question():
    router = CuriosityRouter()
    directive = router.route("What is\n;the risk?")
    assert directive == "Investigate: What is the risk"


def test_consider_curiosity_routes_when_enabled(monkeypatch):
    agent = ExecutiveAgent(
        "exec", enable_curiosity=True, enable_curiosity_routing=True
    )

    def fake_generate_question():
        return "Is there evidence for dark matter?"

    agent.curiosity_agent.generate_question = (
        fake_generate_question  # type: ignore
    )

    called = False

    async def fake_execute_mission(directive, context, session_id=None):
        nonlocal called
        assert "dark matter" in directive
        called = True
        return {"success": True}

    monkeypatch.setattr(agent, "execute_mission", fake_execute_mission)

    asyncio.run(agent._consider_curiosity([]))
    assert called is True


def test_consider_curiosity_routing_disabled(monkeypatch, caplog):
    agent = ExecutiveAgent(
        "exec", enable_curiosity=True, enable_curiosity_routing=False
    )

    def fake_generate_question():
        return "Should not run?"

    agent.curiosity_agent.generate_question = (
        fake_generate_question  # type: ignore
    )

    called = False

    async def fake_execute_mission(
        *args, **kwargs
    ):  # pragma: no cover - should not run
        nonlocal called
        called = True
        return {"success": True}

    monkeypatch.setattr(agent, "execute_mission", fake_execute_mission)

    with caplog.at_level("DEBUG", logger="jarvis.ecosystem.meta_intelligence"):
        asyncio.run(agent._consider_curiosity([]))

    assert called is False
    assert "Curiosity routing disabled" in caplog.text
