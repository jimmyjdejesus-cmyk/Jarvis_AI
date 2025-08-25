import os
import sys
import types
import asyncio

sys.path.append(os.getcwd())

from jarvis.orchestration.orchestrator import MultiAgentOrchestrator


class DummyMCP:
    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        return "{}"


def test_spawn_child_orchestrators_log_aggregation():
    async def run():
        mcp = DummyMCP()
        parent = MultiAgentOrchestrator(mcp)

        dummy_mod = types.ModuleType("jarvis.orchestration.sub_orchestrator")
        class DummySub:
            def __init__(self, *args, **kwargs):
                self.message_bus = parent.message_bus
                self.budgets = {}
            async def coordinate_specialists(self, request, **kwargs):
                return {"request": request}
        dummy_mod.SubOrchestrator = DummySub
        sys.modules["jarvis.orchestration.sub_orchestrator"] = dummy_mod

        for i in range(3):
            parent.spawn_child_orchestrator(f"child{i}", {"allowed_specialists": []})

        assert set(parent.list_child_orchestrators()) == {f"child{i}" for i in range(3)}

        for i in range(3):
            child = parent.child_orchestrators[f"child{i}"]
            await child.log_event("completed", {"i": i}, run_id=f"run{i}")

        memory = parent.message_bus.get_scope_events("global")
        for i in range(3):
            events = [e for e in memory if e["run_id"] == f"run{i}"]
            assert events[0]["type"] == f"child.child{i}.completed"
            assert events[0]["payload"]["i"] == i

    asyncio.run(run())
