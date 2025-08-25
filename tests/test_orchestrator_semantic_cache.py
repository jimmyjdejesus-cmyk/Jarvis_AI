import sys
import types
import pytest

# Stub optional heavy dependencies to keep tests lightweight
sys.modules.setdefault("psutil", types.SimpleNamespace())
sys.modules.setdefault("networkx", types.SimpleNamespace())
dummy_neo4j = types.SimpleNamespace(GraphDatabase=object, Driver=object)
sys.modules.setdefault("neo4j", dummy_neo4j)
sys.modules.setdefault("jarvis.agents", types.SimpleNamespace())

sys.path.append(".")

from jarvis.orchestration.orchestrator import MultiAgentOrchestrator  # noqa: E402


class DummySpecialist:
    def __init__(self):
        self.calls = 0

    async def process_task(self, task, **kwargs):
        self.calls += 1
        return {"specialist": "dummy", "response": task}


@pytest.mark.asyncio
async def test_dispatch_semantic_cache():
    orch = MultiAgentOrchestrator(mcp_client=None)
    dummy = DummySpecialist()
    orch.specialists = {"dummy": dummy}

    first = await orch.dispatch_specialist("dummy", "ping")
    second = await orch.dispatch_specialist("dummy", "ping")

    assert first == second
    assert dummy.calls == 1
