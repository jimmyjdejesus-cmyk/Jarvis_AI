import os
import sys
import pytest

sys.path.append(os.getcwd())

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.orchestration.sub_orchestrator import SubOrchestrator
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator


class DummyMCP:
    """Minimal MCP client stub used for testing."""

    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        return "synthesized"


class DummySpecialist:
    def __init__(self, name: str):
        self.name = name
        self.task_history = []

    async def process_task(self, task, context=None, user_context=None):
        self.task_history.append(task)
        return {
            "specialist": self.name,
            "response": f"{self.name} processed",
            "confidence": 0.9,
        }

    def get_specialization_info(self):
        return {"name": self.name}


class DummySubOrchestrator(SubOrchestrator):
    """SubOrchestrator using dummy specialists for tests."""

    def __init__(
        self,
        mcp_client,
        allowed_specialists=None,
        mission_name=None,
        monitor=None,
        knowledge_graph=None,
    ):
        super().__init__(
            mcp_client,
            mission_name=mission_name,
            allowed_specialists=allowed_specialists,
            monitor=monitor,
            knowledge_graph=knowledge_graph,
        )
        if allowed_specialists:
            self.specialists = {
                name: DummySpecialist(name) for name in allowed_specialists
            }
        else:
            self.specialists = {}


@pytest.mark.asyncio
async def test_executive_agent_spawns_sub_orchestrator():
    mcp = DummyMCP()
    meta = ExecutiveAgent("meta", mcp_client=mcp, orchestrator_cls=DummySubOrchestrator)

    task = {
        "type": "mission_step",
        "step_id": "code_review_step",
        "request": "review the code",
        "specialists": ["code_review"],
    }

    result = await meta.execute_task(task)
    assert result["success"]
    assert "code_review_step" in meta.sub_orchestrators
    assert result["result"]["specialists_used"] == ["code_review"]


@pytest.mark.asyncio
async def test_parent_orchestrator_child_lifecycle():
    mcp = DummyMCP()
    parent = MultiAgentOrchestrator(mcp)

    spec = {"allowed_specialists": ["code_review"]}
    child = parent.create_child_orchestrator("child1", spec)
    assert "child1" in parent.list_child_orchestrators()
    assert parent.remove_child_orchestrator("child1")
    assert "child1" not in parent.list_child_orchestrators()
