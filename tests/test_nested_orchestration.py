import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.orchestration.sub_orchestrator import SubOrchestrator
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator

# --- Mock Fixtures ---

class MockMCPClient:
    """A mock client that returns predictable responses for orchestration tests."""
    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        if "Analyze the following user request" in prompt:
            if "review the code" in prompt:
                return json.dumps({
                    "specialists_needed": ["code_review"],
                    "complexity": "low"
                })
            return json.dumps({"specialists_needed": [], "complexity": "low"})
        elif "code_review processed" in prompt:
            return "synthesized code review response"
        return "synthesized response"

@pytest.fixture
def mcp_client():
    return MockMCPClient()

class DummySpecialist:
    """A dummy specialist for testing."""
    def __init__(self, name: str):
        self.name = name
    async def process_task(self, task, **kwargs):
        return {"specialist": self.name, "response": f"{self.name} processed", "confidence": 0.9}

class DummySubOrchestrator(SubOrchestrator):
    """SubOrchestrator that uses dummy specialists."""
    def __init__(self, mcp_client, **kwargs):
        # The 'specialists' kwarg is added by the ExecutiveAgent logic
        allowed_specialists = kwargs.pop("allowed_specialists", [])
        super().__init__(mcp_client, **kwargs)
        self.specialists = {name: DummySpecialist(name) for name in allowed_specialists}

@pytest.fixture
def executive_agent(mcp_client):
    """An ExecutiveAgent configured with a mock client and dummy orchestrator class."""
    return ExecutiveAgent("meta", mcp_client=mcp_client, orchestrator_cls=DummySubOrchestrator)

# --- Tests ---

@pytest.mark.asyncio
async def test_executive_agent_spawns_sub_orchestrator(executive_agent):
    """Test that the ExecutiveAgent can spawn and use a sub-orchestrator for a mission step."""
    task = {
        "type": "mission_step",
        "step_id": "code_review_step",
        "request": "review the code",
        "specialists": ["code_review"],
    }

    result = await executive_agent.execute_task(task)

    assert result["success"]
    assert "code_review_step" in executive_agent.sub_orchestrators
    # Check that the result from the dummy specialist was propagated up
    assert result["result"]["synthesized_response"] == "synthesized code review response"

@pytest.mark.asyncio
async def test_parent_orchestrator_child_lifecycle(mcp_client):
    """Test that a parent orchestrator can create and remove child orchestrators."""
    parent = MultiAgentOrchestrator(mcp_client=mcp_client, specialists={
        "code_review": DummySpecialist("code_review")
    })

    spec = {"allowed_specialists": ["code_review"]}
    child = parent.create_child_orchestrator("child1", spec)
    assert "child1" in parent.list_child_orchestrators()
    assert parent.remove_child_orchestrator("child1")
    assert "child1" not in parent.list_child_orchestrators()

@pytest.mark.asyncio
async def test_recursive_orchestrators_not_implemented(mcp_client):
    """
    This test was complex and relied on monkeypatching. The underlying feature
    of passing child_specs to the constructor was removed in a refactor.
    A simple lifecycle test is more appropriate now.
    """
    parent = MultiAgentOrchestrator(mcp_client=mcp_client, specialists={
        "a": DummySpecialist("a"),
        "b": DummySpecialist("b"),
    })
    parent.create_child_orchestrator("child", {"allowed_specialists": ["a"]})
    child = parent.child_orchestrators["child"]
    child.create_child_orchestrator("grandchild", {"allowed_specialists": ["b"]})

    assert "grandchild" in child.list_child_orchestrators()
