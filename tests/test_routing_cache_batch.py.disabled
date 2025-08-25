import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import types
sys.modules.setdefault("networkx", types.SimpleNamespace())
dummy_neo4j = types.SimpleNamespace(GraphDatabase=object, Driver=object)
sys.modules.setdefault("neo4j", dummy_neo4j)

from jarvis.mcp.client import MCPClient
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator
from jarvis.orchestration.path_memory import PathMemory
from jarvis.homeostasis.monitor import SystemMonitor, ResourceSnapshot


class DummyMonitor(SystemMonitor):
    def snapshot(self) -> ResourceSnapshot:  # type: ignore[override]
        return ResourceSnapshot(cpu=90, memory=10, api_tokens=0)


@pytest.mark.asyncio
async def test_dynamic_model_routing_prefers_local():
    monitor = DummyMonitor()
    client = MCPClient(monitor=monitor)
    orchestrator = MultiAgentOrchestrator(client, monitor=monitor)
    specialist = orchestrator.specialists["code_review"]
    models = orchestrator._route_model_preferences(specialist, "low")
    assert specialist._get_server_for_model(models[0]) == "ollama"


@pytest.mark.asyncio
async def test_mcp_cache_avoids_duplicate_calls(monkeypatch):
    client = MCPClient()
    client.active_connections["ollama"] = ""
    calls = {"n": 0}

    async def fake_generate(model, prompt):
        calls["n"] += 1
        return "resp"

    client._generate_ollama_response = fake_generate  # type: ignore

    await client.generate_response("ollama", "llama3.2", "hi")
    await client.generate_response("ollama", "llama3.2", "hi")
    assert calls["n"] == 1


class DummyClient(MCPClient):
    def __init__(self):
        super().__init__(monitor=None)
        self.active_connections["ollama"] = ""
        self.batch_calls = []

    async def generate_response(self, server, model, prompt):
        return "ok"

    async def generate_response_batch(self, server, model, prompts):
        self.batch_calls.append((server, model, prompts))
        return ["ok" for _ in prompts]


@pytest.mark.asyncio
async def test_parallel_batching_uses_single_batch_call():
    client = DummyClient()
    orchestrator = MultiAgentOrchestrator(client)
    orchestrator.specialists["security"].preferred_models = ["codellama"]
    analysis = {"specialists_needed": ["code_review", "security"], "complexity": "low"}
    result = await orchestrator._parallel_specialist_analysis("req", analysis, PathMemory())
    assert len(client.batch_calls) == 1
    assert set(result["results"].keys()) == {"code_review", "security"}
