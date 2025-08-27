import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from jarvis.orchestration.orchestrator import MultiAgentOrchestrator

class DummyMcpClient:
    async def generate_response(self, server, model, prompt):
        if "Analyze" in prompt:
            return '{"specialists_needed": ["testspecialist"], "complexity": "low"}'
        if "constitutional critic" in prompt:
            return '{"veto": false, "violations": []}'
        return "response"

class DummySpecialist:
    def __init__(self, name="test_specialist"):
        self.name = name

    async def process_task(self, task, **kwargs):
        return {"response": f"{self.name} processed {task}"}

@pytest.mark.asyncio
async def test_orchestrator_with_critic():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client)
    orchestrator.specialists = {"testspecialist": DummySpecialist()}

    result = await orchestrator.coordinate_specialists("test request")
    assert result["synthesized_response"] == "response"

@pytest.mark.asyncio
async def test_orchestrator_with_critic_veto():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client)
    orchestrator.specialists = {"testspecialist": DummySpecialist()}

    async def mock_review(plan):
        return {"veto": True, "violations": ["test violation"]}

    orchestrator.critic.review = mock_review

    result = await orchestrator.coordinate_specialists("test request")
    assert result["error"] is True
    assert "test violation" in result["synthesized_response"]

@pytest.mark.asyncio
async def test_dispatch_with_retry():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client)

    specialist = DummySpecialist()
    specialist.process_task = AsyncMock(
        side_effect=[Exception("fail"), {"response": "success"}]
    )
    orchestrator.specialists = {"testspecialist": specialist}

    with pytest.raises(Exception) as e:
        await orchestrator.dispatch_specialist("test_specialist", "test")
    assert "Task failed after 3 retries" in str(e.value)
    assert specialist.process_task.call_count == 3

@pytest.mark.asyncio
async def test_dispatch_with_timeout():
    mcp_client = DummyMcpClient()
    orchestrator = MultiAgentOrchestrator(mcp_client)

    async def slow_task(*args, **kwargs):
        await asyncio.sleep(0.2)
        return {"response": "success"}

    specialist = DummySpecialist()
    specialist.process_task = slow_task
    orchestrator.specialists = {"test_specialist": specialist}

    with pytest.raises(Exception) as e:
        await orchestrator.dispatch_specialist("test_specialist", "test")

    assert "Task failed after 3 retries" in str(e.value)
