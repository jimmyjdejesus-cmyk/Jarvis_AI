import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from jarvis.mcp.model_router import ModelRouter


class DummyClient:
    async def generate_response(self, server, model, prompt):
        return f"{server}:{model}"

    async def check_server_health(self, server):
        return True


@pytest.mark.asyncio
async def test_policy_routing():
    client = DummyClient()
    router = ModelRouter(client)

    resp = await router.route_to_best_model(
        "hi", task_type="general", complexity="high", budget="aggressive"
    )
    assert resp.startswith("openai:gpt-4")
    assert "GPT-4" in router.last_justification

    resp2 = await router.route_to_best_model(
        "hi", task_type="general", complexity="low", budget="conservative"
    )
    assert resp2.startswith("ollama:llama3.2")
    assert "local model" in router.last_justification
