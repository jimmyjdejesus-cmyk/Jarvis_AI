import json
import pytest
from jarvis.ecosystem.meta_intelligence import ExecutiveAgent


class DummyMemory:
    """Simple in-memory store for testing."""

    def __init__(self) -> None:
        self.store = []

    def add(self, project: str, session: str, text: str, metadata=None) -> None:
        self.store.append((project, session, text, metadata))

    def query(self, project: str, session: str, text: str, top_k: int = 5):
        return [
            {"text": t, "metadata": m}
            for p, s, t, m in self.store
            if p == project and s == session
        ]


class DummyOrchestrator:
    """Minimal orchestrator returning canned responses."""

    def __init__(self, mcp_client, **kwargs):
        pass

    async def coordinate_specialists(self, request, code=None, user_context=None, context=None, novelty_boost: float = 0.0):
        return {"output": f"{request} done"}


@pytest.mark.asyncio
async def test_facts_persist_across_steps():
    memory = DummyMemory()
    agent = ExecutiveAgent("exec", orchestrator_cls=DummyOrchestrator, memory_manager=memory)
    agent.constitutional_critic = type("C", (), {"review": lambda self, _: {}})()

    await agent._handle_mission_step({"step_id": "s1", "request": "first"})
    await agent._handle_mission_step({"step_id": "s2", "request": "second"})

    stored = memory.query("mission", "s1", "")
    assert stored and "first" in stored[0]["text"]

    facts1 = agent.knowledge_graph.get_facts("s1")
    facts2 = agent.knowledge_graph.get_facts("s2")

    assert json.loads(facts1[0][2])["output"] == "first done"
    assert json.loads(facts2[0][2])["output"] == "second done"
