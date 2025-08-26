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

# Stub security manager to avoid bcrypt dependency
sec_pkg = types.ModuleType("jarvis.auth.security_manager")


class _DummySecurityManager:
    pass


def get_security_manager():
    return _DummySecurityManager()


sec_pkg.SecurityManager = _DummySecurityManager
sec_pkg.get_security_manager = get_security_manager
sys.modules["jarvis.auth.security_manager"] = sec_pkg

# Stub knowledge graph to avoid networkx dependency
# Stub knowledge graph and hypergraph to avoid networkx dependency
kg_pkg = types.ModuleType("jarvis.world_model.knowledge_graph")
hg_pkg = types.ModuleType("jarvis.world_model.hypergraph")


class _DummyKG:
    pass


class _DummyHG:
    pass


kg_pkg.KnowledgeGraph = _DummyKG
hg_pkg.HierarchicalHypergraph = _DummyHG
sys.modules["jarvis.world_model.knowledge_graph"] = kg_pkg
sys.modules["jarvis.world_model.hypergraph"] = hg_pkg
wm_pkg = types.ModuleType("jarvis.world_model")
wm_pkg.KnowledgeGraph = _DummyKG
wm_pkg.HierarchicalHypergraph = _DummyHG
sys.modules["jarvis.world_model"] = wm_pkg

# Stub system monitor to avoid psutil dependency
mon_pkg = types.ModuleType("jarvis.homeostasis.monitor")


class _DummyMonitor:
    pass


mon_pkg.SystemMonitor = _DummyMonitor
sys.modules["jarvis.homeostasis.monitor"] = mon_pkg
homeo_pkg = types.ModuleType("jarvis.homeostasis")
homeo_pkg.SystemMonitor = _DummyMonitor
sys.modules["jarvis.homeostasis"] = homeo_pkg

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
