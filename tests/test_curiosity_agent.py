import os
import sys
import asyncio
import types

sys.path.append(os.getcwd())

# Stub orchestration modules
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

from jarvis.agents.curiosity_agent import CuriosityAgent
from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.world_model.hypergraph import HierarchicalHypergraph


def test_curiosity_agent_generates_question() -> None:
    hg = HierarchicalHypergraph()
    hg.layers[3]["torch_linear_performance"] = {
        "description": "torch.nn.Linear layer on ARM",
        "confidence": 0.3,
    }
    agent = CuriosityAgent(hg, threshold=0.5)
    question = agent.generate_question()
    assert question and "torch.nn.Linear" in question


def test_executive_agent_pursues_curiosity() -> None:
    hg = HierarchicalHypergraph()
    hg.layers[1]["mystery"] = {"description": "unknown", "confidence": 0.2}
    exec_agent = ExecutiveAgent("meta_test")
    exec_agent.hypergraph = hg
    exec_agent.curiosity_agent = CuriosityAgent(hg, threshold=0.5)
    result = asyncio.run(exec_agent.execute_task({"type": "pursue_curiosity"}))
    assert result["success"]
    assert result.get("directive")
