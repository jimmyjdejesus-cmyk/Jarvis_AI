import os
import sys
import asyncio
import types

sys.path.append(os.getcwd())

# Stub orchestration modules to avoid importing heavy dependencies
orch_pkg = types.ModuleType("jarvis.orchestration")
orch_pkg.__path__ = []


class _DummyOrchestrator:
    async def coordinate_specialists(self, *args, **kwargs):
        return {}


orch_pkg.MultiAgentOrchestrator = _DummyOrchestrator
orch_pkg.SubOrchestrator = _DummyOrchestrator
sys.modules["jarvis.orchestration"] = orch_pkg
stub_orch = types.ModuleType("jarvis.orchestration.orchestrator")
stub_orch.MultiAgentOrchestrator = _DummyOrchestrator
stub_orch.SubOrchestrator = _DummyOrchestrator
stub_orch.AgentSpec = dict
stub_orch.DynamicOrchestrator = _DummyOrchestrator
sys.modules["jarvis.orchestration.orchestrator"] = stub_orch
sub_pkg = types.ModuleType("jarvis.orchestration.sub_orchestrator")
sub_pkg.SubOrchestrator = _DummyOrchestrator
sys.modules["jarvis.orchestration.sub_orchestrator"] = sub_pkg

# Stub security manager to avoid bcrypt dependency
sec_pkg = types.ModuleType("jarvis.auth.security_manager")


class _DummySecurityManager:
    pass


def get_security_manager():
    return _DummySecurityManager()


sec_pkg.SecurityManager = _DummySecurityManager
sec_pkg.get_security_manager = get_security_manager
sys.modules["jarvis.auth.security_manager"] = sec_pkg

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
wm_pkg.__path__ = []
wm_pkg.KnowledgeGraph = _DummyKG
wm_pkg.HierarchicalHypergraph = _DummyHG
sys.modules["jarvis.world_model"] = wm_pkg
predict_pkg = types.ModuleType("jarvis.world_model.predictive_simulation")
class _DummyPredictor:
    pass
predict_pkg.PredictiveSimulator = _DummyPredictor
sys.modules["jarvis.world_model.predictive_simulation"] = predict_pkg

# Stub system monitor to avoid psutil dependency
mon_pkg = types.ModuleType("jarvis.homeostasis.monitor")


class _DummyMonitor:
    pass


mon_pkg.SystemMonitor = _DummyMonitor
sys.modules["jarvis.homeostasis.monitor"] = mon_pkg
homeo_pkg = types.ModuleType("jarvis.homeostasis")
homeo_pkg.SystemMonitor = _DummyMonitor
sys.modules["jarvis.homeostasis"] = homeo_pkg

# Stub memory project memory to avoid chromadb dependency
mem_pkg = types.ModuleType("jarvis.memory.project_memory")


class _DummyMemoryManager:
    pass


class _DummyProjectMemory(_DummyMemoryManager):
    pass


mem_pkg.MemoryManager = _DummyMemoryManager
mem_pkg.ProjectMemory = _DummyProjectMemory
sys.modules["jarvis.memory.project_memory"] = mem_pkg

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.agents.critics import CriticVerdict, WhiteGate


class DummyRedCritic:
    def __init__(self):
        self.calls = 0

    async def review(self, artifact, trace):
        self.calls += 1
        if self.calls == 1:
            return CriticVerdict(False, ["fix issue"], 0.0, "needs fix")
        return CriticVerdict(True, [], 0.0, "ok")


class DummyBlueCritic:
    def review(self, artifact, trace):
        return CriticVerdict(True, [], 0.6, "risky")


def test_fix_loop_and_hitl():
    agent = ExecutiveAgent("meta", enable_red_team=True, enable_blue_team=True)
    agent.red_team = DummyRedCritic()
    agent.blue_team = DummyBlueCritic()
    agent.white_gate = WhiteGate(risk_threshold=0.5)
    result = asyncio.run(agent.execute_task({"type": "unknown"}))
    assert agent.red_team.calls == 2
    assert result["critic"]["white"]["approved"] is False
    assert "HITL" in result["critic"]["white"]["notes"]
