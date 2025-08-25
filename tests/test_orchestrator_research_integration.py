"""Integration test for Orchestrator using ResearchAgent."""

from __future__ import annotations

import sys
import types
from unittest.mock import patch, Mock
from pathlib import Path

# Stub out jarvis package structure to avoid heavy imports
root = Path(__file__).resolve().parents[1]
jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(root / "jarvis")]
sys.modules.setdefault("jarvis", jarvis_pkg)

tools_pkg = types.ModuleType("jarvis.tools")
tools_pkg.__path__ = [str(root / "jarvis" / "tools")]
sys.modules.setdefault("jarvis.tools", tools_pkg)

orch_pkg = types.ModuleType("jarvis.orchestration")
orch_pkg.__path__ = [str(root / "jarvis" / "orchestration")]
sys.modules.setdefault("jarvis.orchestration", orch_pkg)

memory_pkg = types.ModuleType("jarvis.memory")
memory_pkg.__path__ = [str(root / "jarvis" / "memory")]
sys.modules.setdefault("jarvis.memory", memory_pkg)

# Stub external memory_service dependency
memory_service = types.ModuleType("memory_service")
dummy = type("Dummy", (), {})
memory_service.Metrics = memory_service.NegativeCheck = dummy
memory_service.Outcome = memory_service.PathRecord = memory_service.PathSignature = dummy
memory_service.avoid_negative = lambda *a, **k: None
memory_service.record_path = lambda *a, **k: None
sys.modules.setdefault("memory_service", memory_service)

# Stub HITL policy dependency
agent_pkg = types.ModuleType("agent")
agent_pkg.__path__ = []
sys.modules.setdefault("agent", agent_pkg)

hitl_pkg = types.ModuleType("agent.hitl")
hitl_pkg.__path__ = []
sys.modules.setdefault("agent.hitl", hitl_pkg)

policy_mod = types.ModuleType("agent.hitl.policy")
class HITLPolicy: ...
class ApprovalCallback: ...
policy_mod.HITLPolicy = HITLPolicy
policy_mod.ApprovalCallback = ApprovalCallback
sys.modules.setdefault("agent.hitl.policy", policy_mod)

# Stub redis client used by MissionPlanner
redis_mod = types.ModuleType("redis")
class Redis:
    def __init__(self, *a, **k):
        pass
    def rpush(self, *a, **k):
        pass
    def lpop(self, *a, **k):
        return None
    def llen(self, *a, **k):
        return 0
redis_mod.Redis = Redis
redis_mod.RedisError = Exception
sys.modules.setdefault("redis", redis_mod)

# Stub ecosystem to avoid heavy world model imports
ecosystem_mod = types.ModuleType("jarvis.ecosystem")
ecosystem_mod.superintelligence = object()
sys.modules.setdefault("jarvis.ecosystem", ecosystem_mod)

from jarvis.orchestration.agents import OrchestratorAgent


def _make_response(text: str) -> Mock:
    resp = Mock()
    resp.status_code = 200
    resp.text = text
    resp.raise_for_status = Mock()
    return resp


class DummyMultiTeamOrchestrator:
    def __init__(self, orchestrator_agent, evaluator=None):
        self.yellow_agent = orchestrator_agent.teams["competitive_pair"][0]

    def run(self, objective: str):
        return {"competitive_pair": self.yellow_agent.run(objective, {})}


def test_orchestrator_propagates_research_metadata(tmp_path: Path) -> None:
    """Orchestrator returns research gaps and confidence from Yellow team."""

    empty_search_html = "<html></html>"

    with patch("jarvis.tools.web_tools.requests.get", side_effect=[_make_response(empty_search_html)]):
        with patch("jarvis.orchestration.graph.MultiTeamOrchestrator", DummyMultiTeamOrchestrator):
            orch = OrchestratorAgent(meta_agent=types.SimpleNamespace(), objective="Widget", directory=tmp_path)
            result = orch.run()

    report = result["competitive_pair"]["research_summary"]
    assert "No sources found" in report["gaps"]
    assert report["confidence"] == 0.5
