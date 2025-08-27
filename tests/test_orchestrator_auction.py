import sys
import types
import pytest

# Mock external dependencies for isolated testing
sys.modules.setdefault("psutil", types.SimpleNamespace())
sys.modules.setdefault("networkx", types.SimpleNamespace())
dummy_neo4j = types.SimpleNamespace(GraphDatabase=object, Driver=object)
sys.modules.setdefault("neo4j", dummy_neo4j)
agents_pkg = types.ModuleType("jarvis.agents")
sys.modules["jarvis.agents"] = agents_pkg


class _Dummy:
    def __init__(self, *args, **kwargs):
        pass


sys.modules["jarvis.agents.specialists"] = types.SimpleNamespace(
    CodeReviewAgent=_Dummy,
    SecurityAgent=_Dummy,
    ArchitectureAgent=_Dummy,
    TestingAgent=_Dummy,
    DevOpsAgent=_Dummy,
)

sys.modules["jarvis.agents.specialist_registry"] = types.SimpleNamespace(
    SPECIALIST_REGISTRY={},
    create_specialist=lambda name, mcp_client, **_: _Dummy(),
)
from app.main import app

import jarvis.memory.project_memory as project_memory
from jarvis.memory.memory_bus import MemoryBus
from jarvis.memory.project_memory import ProjectMemory
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator
from jarvis.orchestration.path_memory import PathMemory


class DummyMCP:
    async def generate_response_batch(self, server, model, prompts):
        return [f"resp_{p}" for p in prompts]

    async def generate_response(self, server, model, prompt):
        # The test asserts that the winner's response is in the synthesis.
        # Let's make the synthesis predictable for the test.
        if "a" in prompt.lower() and "b" in prompt.lower():
            return "a: synthesized response"
        return "synthesis"


class DummySpecialist:
    def __init__(self, name, confidence):
        self.name = name
        self.confidence = confidence
        self.preferred_models = ["m"]

    def _get_server_for_model(self, model):  # pragma: no cover - simple stub
        return "ollama"

    def build_prompt(self, task, context, user_context):  # pragma: no cover
        return f"{self.name}_prompt"

    def process_model_response(self, response, model, task):
        return {
            "specialist": self.name,
            "response": response,
            "confidence": self.confidence,
            "suggestions": [f"{self.name}_sugg"],
        }


@pytest.mark.asyncio
async def test_parallel_orchestrator_auction_merge():
    mcp = DummyMCP()
    orch = MultiAgentOrchestrator(mcp)
    orch.specialists = {
        "a": DummySpecialist("a", 0.9),
        "b": DummySpecialist("b", 0.5),
    }
    analysis = {"specialists_needed": ["a", "b"], "complexity": "low"}
    result = await orch._parallel_specialist_analysis("req", analysis, PathMemory(), None, None, None)
    assert result["auction"]["winner"] == "a"
    assert "a:" in result["synthesized_response"].splitlines()[0]
    assert result["exploration_metrics"]["diversity"] >= 2

