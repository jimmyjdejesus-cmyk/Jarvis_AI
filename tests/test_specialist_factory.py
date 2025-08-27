import asyncio
import importlib.util
import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Stub minimal jarvis package to avoid heavy imports
jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(ROOT / "jarvis")]
sys.modules["jarvis"] = jarvis_pkg

agents_pkg = types.ModuleType("jarvis.agents")
agents_pkg.__path__ = [str(ROOT / "jarvis" / "agents")]
sys.modules["jarvis.agents"] = agents_pkg

# Load real agent_resources for AgentCapability
spec_ar = importlib.util.spec_from_file_location(
    "jarvis.agents.agent_resources", ROOT / "jarvis" / "agents" / "agent_resources.py"
)
agent_resources = importlib.util.module_from_spec(spec_ar)
sys.modules["jarvis.agents.agent_resources"] = agent_resources
spec_ar.loader.exec_module(agent_resources)

# Provide a stub KnowledgeGraph
kg_mod = types.ModuleType("jarvis.world_model.knowledge_graph")
class _KG:
    pass
kg_mod.KnowledgeGraph = _KG
sys.modules["jarvis.world_model.knowledge_graph"] = kg_mod

# Stub execution sandbox
tools_pkg = types.ModuleType("jarvis.tools")
sys.modules["jarvis.tools"] = tools_pkg

exec_mod = types.ModuleType("jarvis.tools.execution_sandbox")

class _ExecResult:
    def __init__(self):
        self.stdout = ""
        self.stderr = ""
        self.exit_code = 0


def run_python_code(_code: str, timeout: int = 10) -> _ExecResult:
    return _ExecResult()


exec_mod.run_python_code = run_python_code
sys.modules["jarvis.tools.execution_sandbox"] = exec_mod

# Ensure stale modules from previous tests don't interfere
sys.modules.pop("jarvis.agents.specialists", None)

# Import domain specialists and registry
spec_ds = importlib.util.spec_from_file_location(
    "jarvis.agents.domain_specialists", ROOT / "jarvis" / "agents" / "domain_specialists.py"
)
domain_specialists = importlib.util.module_from_spec(spec_ds)
sys.modules["jarvis.agents.domain_specialists"] = domain_specialists
spec_ds.loader.exec_module(domain_specialists)

spec_reg = importlib.util.spec_from_file_location(
    "jarvis.agents.specialist_registry", ROOT / "jarvis" / "agents" / "specialist_registry.py"
)
registry = importlib.util.module_from_spec(spec_reg)
sys.modules["jarvis.agents.specialist_registry"] = registry
spec_reg.loader.exec_module(registry)

create_specialist = registry.create_specialist


@pytest.mark.parametrize(
    "name, method, args, header",
    [
        ("docs", "create_report", ("system overview",), "REPORT REQUEST"),
        ("database", "optimize_query", ("SELECT 1", None), "QUERY OPTIMIZATION REQUEST"),
        ("security", "penetration_test", ("test system",), "PENETRATION TEST REQUEST"),
        ("localization", "translate_content", ("Hello", "es"), "LOCALIZATION REQUEST"),
        ("code_review", "review_code", ("print('hi')",), "CODE REVIEW REQUEST"),
    ],
)
def test_specialist_factory(monkeypatch, name, method, args, header):
    captured = {}

    async def fake_process(self, task):
        captured["task"] = task
        return {"ok": True}

    # Patch process_task for the specific specialist class
    specialist_cls = registry.SPECIALIST_REGISTRY[name]
    monkeypatch.setattr(specialist_cls, "process_task", fake_process, raising=False)

    agent = create_specialist(name, mcp_client=None)
    result = asyncio.run(getattr(agent, method)(*args))

    assert result == {"ok": True}
    assert header in captured["task"]


def test_cloud_cost_agent(monkeypatch):
    """Ensure the CloudCostOptimizerAgent loads without heavy deps."""
    captured = {}

    async def fake_process(self, task):
        captured["task"] = task
        return {"ok": True}

    specialist_cls = registry.SPECIALIST_REGISTRY["cloud_cost"]
    monkeypatch.setattr(specialist_cls, "process_task", fake_process, raising=False)

    class _StubMCP:
        async def call_model(self, *_args, **_kwargs):
            return {}

    agent = create_specialist("cloud_cost", mcp_client=_StubMCP())
    result = asyncio.run(agent.analyze_usage("usage data"))

    assert result == {"ok": True}
    assert "CLOUD COST ANALYSIS REQUEST" in captured["task"]
