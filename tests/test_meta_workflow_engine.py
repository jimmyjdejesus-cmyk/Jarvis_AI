import asyncio
import sys
import types

import pytest

sys.modules.setdefault("jarvis.agents.coding_agent", types.ModuleType("coding_agent"))

memory_service = types.ModuleType("memory_service")
memory_service.Metrics = lambda *a, **k: None
memory_service.NegativeCheck = lambda *a, **k: None
memory_service.Outcome = lambda *a, **k: None
memory_service.PathRecord = lambda *a, **k: None
memory_service.PathSignature = lambda *a, **k: None
memory_service.avoid_negative = lambda *a, **k: {}
memory_service.record_path = lambda *a, **k: None
memory_service.vector_store = None
sys.modules["memory_service"] = memory_service

mm_module = types.ModuleType("jarvis.memory.project_memory")
class _MM: ...
class _PM(_MM):
    def __init__(self, *a, **k):
        pass
mm_module.MemoryManager = _MM
mm_module.ProjectMemory = _PM
sys.modules["jarvis.memory.project_memory"] = mm_module

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.orchestration.mission import MissionDAG, MissionNode


class DummyPlanner:
    def plan(self, goal: str, context):
        nodes = {
            "a": MissionNode(step_id="a", capability="cap", team_scope="team"),
            "b": MissionNode(step_id="b", capability="cap", team_scope="team"),
            "c": MissionNode(step_id="c", capability="cap", team_scope="team", deps=["a", "b"]),
        }
        edges = [("a", "c"), ("b", "c")]
        return MissionDAG(mission_id="m1", nodes=nodes, edges=edges, rationale="")


def test_execute_mission_builds_workflow_graph():
    agent = ExecutiveAgent("tester", mission_planner=DummyPlanner())

    class DummyCritic:
        async def review(self, _plan):
            return {"veto": False}

    agent.constitutional_critic = DummyCritic()

    async def dummy_handle(self, step):
        await asyncio.sleep(0.01)
        return {"success": True, "step_id": step["step_id"]}

    agent._handle_mission_step = types.MethodType(dummy_handle, agent)

    result = asyncio.run(agent.execute_mission("do things", {}))
    assert result["success"]

    graph = agent.get_execution_graph()
    assert graph["status"] == "completed"
    assert set(graph["nodes"]) == {"a", "b", "c"}
    assert ("a", "c") in graph["edges"] and ("b", "c") in graph["edges"]
