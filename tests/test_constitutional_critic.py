import os
import sys
import asyncio
import types

sys.path.append(os.getcwd())

# Stub orchestration modules to avoid importing heavy dependencies
orch_pkg = types.ModuleType("jarvis.orchestration")

class _DummyOrchestrator:
    async def coordinate_specialists(self, *args, **kwargs):
        return {}

orch_pkg.MultiAgentOrchestrator = _DummyOrchestrator
orch_pkg.SubOrchestrator = _DummyOrchestrator
sys.modules["jarvis.orchestration"] = orch_pkg
stub_orch = types.ModuleType("jarvis.orchestration.orchestrator")
stub_orch.MultiAgentOrchestrator = _DummyOrchestrator
stub_orch.SubOrchestrator = _DummyOrchestrator
sys.modules["jarvis.orchestration.orchestrator"] = stub_orch

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent


def test_constitutional_critic_vetoes_blocked_plan() -> None:
    agent = ExecutiveAgent("exec_test")

    def fake_plan(goal: str, strategy: str = "standard"):
        return ["DROP TABLE users"]

    agent.mission_planner.plan = fake_plan  # type: ignore
    result = agent.manage_directive("bad goal")
    assert result["success"] is False
    assert result["critique"]["veto"] is True


def test_constitutional_critic_blocks_mission_step() -> None:
    agent = ExecutiveAgent("exec_test")

    def fake_plan(goal: str, strategy: str = "standard"):
        return ["DROP TABLE users"]

    agent.mission_planner.plan = fake_plan  # type: ignore
    result = asyncio.run(agent._handle_mission_step({"request": "danger"}))
    assert result["success"] is False
    assert result["critique"]["veto"] is True
