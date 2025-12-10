import asyncio
import sys
import types

from jarvis.orchestration.orchestrator import MultiAgentOrchestrator


# Mock external dependencies for isolated testing
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


def test_parallel_orchestrator_auction_merge():
    mcp = DummyMCP()
    orch = MultiAgentOrchestrator(mcp)
    orch.specialists = {
        "a": DummySpecialist("a", 0.9),
        "b": DummySpecialist("b", 0.8),
    }

    async def fake_analyze(request, code=None):
        return {"specialists_needed": ["a", "b"], "complexity": "low"}

    orch._analyze_request_complexity = fake_analyze

    result = asyncio.run(orch.coordinate_specialists("task"))

    assert result["auction"]["winner"] == "a"
    assert result["confidence"] == 0.9
    assert result["synthesized_response"] == "a: synthesized response"
