from unittest.mock import MagicMock

import pytest

from jarvis.orchestration.orchestrator import (
    MultiAgentOrchestrator,
    StepContext,
)


class DummyMcpClient:
    async def generate_response(self, server, model, prompt):
        if "Analyze" in prompt:
            return (
                '{"specialists_needed": ["testspecialist"], '
                '"complexity": "low"}'
            )
        if "constitutional critic" in prompt:
            return '{"veto": false, "violations": []}'
        return "response"


class DummySpecialist:
    async def process_task(self, task, **kwargs):
        return {"response": "response", "confidence": 0.9}


@pytest.mark.asyncio
async def test_orchestrator_updates_policy_and_memory():
    mcp_client = DummyMcpClient()
    memory = MagicMock()
    memory.query.return_value = []
    hypergraph = MagicMock()
    hypergraph.query.return_value = None
    policy = MagicMock()

    orchestrator = MultiAgentOrchestrator(
        mcp_client,
        specialists={},
        memory=memory,
        hypergraph=hypergraph,
        policy_optimizer=policy,
    )
    orchestrator.specialists = {"testspecialist": DummySpecialist()}

    ctx = StepContext(request="do stuff", budgets={"run_id": "1"})
    result = await orchestrator.run_step(ctx)

    memory.query.assert_called()
    memory.add.assert_called()
    assert hypergraph.update_node.called
    policy.update_strategy.assert_called_with("do stuff", 1.0)
    assert result.data["synthesized_response"] == "response"
