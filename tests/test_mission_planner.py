import json
import sys
import types
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Stub out jarvis package to avoid heavy imports
jarvis_pkg = types.ModuleType("jarvis")
sys.modules["jarvis"] = jarvis_pkg
models_pkg = types.ModuleType("jarvis.models")
jarvis_pkg.models = models_pkg
sys.modules["jarvis.models"] = models_pkg
client_mod = types.ModuleType("jarvis.models.client")
models_pkg.client = client_mod
sys.modules["jarvis.models.client"] = client_mod
class _DefaultClient:
    def generate_response(self, model, prompt):
        return ""

client_mod.model_client = _DefaultClient()

spec = importlib.util.spec_from_file_location(
    "jarvis.agents.mission_planner", ROOT / "jarvis" / "agents" / "mission_planner.py"
)
mission_planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mission_planner)
sys.modules["jarvis.agents.mission_planner"] = mission_planner
agents_pkg = types.ModuleType("jarvis.agents")
agents_pkg.mission_planner = mission_planner
sys.modules["jarvis.agents"] = agents_pkg

spec2 = importlib.util.spec_from_file_location(
    "jarvis.persistence.session", ROOT / "jarvis" / "persistence" / "session.py"
)
session_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(session_module)
sys.modules["jarvis.persistence.session"] = session_module
persistence_pkg = types.ModuleType("jarvis.persistence")
persistence_pkg.session = session_module
sys.modules["jarvis.persistence"] = persistence_pkg

# Stub tools and world model to satisfy ExecutiveAgent imports
tools_pkg = types.ModuleType("jarvis.tools")
sys.modules["jarvis.tools"] = tools_pkg
repo_indexer_mod = types.ModuleType("jarvis.tools.repository_indexer")

class _DummyIndexer:
    def __init__(self, *args, **kwargs):
        pass

    def build_index(self):
        pass

    def index_repository(self, graph):
        pass

repo_indexer_mod.RepositoryIndexer = _DummyIndexer
tools_pkg.repository_indexer = repo_indexer_mod
sys.modules["jarvis.tools.repository_indexer"] = repo_indexer_mod

world_pkg = types.ModuleType("jarvis.world_model")
kg_mod = types.ModuleType("jarvis.world_model.knowledge_graph")

class _DummyKG:
    def populate_from_indexer(self, indexer):
        pass

world_pkg.knowledge_graph = kg_mod
kg_mod.KnowledgeGraph = _DummyKG
sys.modules["jarvis.world_model"] = world_pkg
sys.modules["jarvis.world_model.knowledge_graph"] = kg_mod

home_pkg = types.ModuleType("jarvis.homeostasis")
monitor_mod = types.ModuleType("jarvis.homeostasis.monitor")

class _DummyMonitor:
    pass

monitor_mod.SystemMonitor = _DummyMonitor
home_pkg.monitor = monitor_mod
sys.modules["jarvis.homeostasis"] = home_pkg
sys.modules["jarvis.homeostasis.monitor"] = monitor_mod

# Stub orchestrator to satisfy ExecutiveAgent imports
orchestr_pkg = types.ModuleType("jarvis.orchestration")
orchestr_mod = types.ModuleType("jarvis.orchestration.orchestrator")

class _DummyOrchestrator:
    def __init__(self, *args, **kwargs):
        pass

    async def coordinate_specialists(self, *args, **kwargs):
        return {}

orchestr_mod.MultiAgentOrchestrator = _DummyOrchestrator
orchestr_pkg.orchestrator = orchestr_mod
orchestr_pkg.MultiAgentOrchestrator = _DummyOrchestrator
orchestr_pkg.SubOrchestrator = _DummyOrchestrator
sys.modules["jarvis.orchestration"] = orchestr_pkg
sys.modules["jarvis.orchestration.orchestrator"] = orchestr_mod

spec3 = importlib.util.spec_from_file_location(
    "jarvis.ecosystem.meta_intelligence", ROOT / "jarvis" / "ecosystem" / "meta_intelligence.py"
)
meta_module = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(meta_module)
ecosystem_pkg = types.ModuleType("jarvis.ecosystem")
ecosystem_pkg.meta_intelligence = meta_module
sys.modules["jarvis.ecosystem"] = ecosystem_pkg
sys.modules["jarvis.ecosystem.meta_intelligence"] = meta_module

MissionPlanner = mission_planner.MissionPlanner
ExecutiveAgent = meta_module.ExecutiveAgent


class DummyClient:
    def __init__(self, response: str):
        self.response = response

    def generate_response(self, model: str, prompt: str):
        return self.response


def test_mission_planner_decomposes_goal():
    client = DummyClient("1. Gather requirements\n2. Design architecture\n3. Implement features")
    planner = MissionPlanner(client)
    tasks = planner.plan("Build an app")
    assert tasks == [
        "Gather requirements",
        "Design architecture",
        "Implement features",
    ]


def test_executive_agent_manage_directive_builds_graph(tmp_path):
    class StubPlanner(MissionPlanner):
        def __init__(self):
            pass

        def plan(self, goal: str):
            return ["Task A", "Task B"]

        def to_graph(self, tasks):
            return {
                "nodes": {"task_1": {"description": "Task A"}, "task_2": {"description": "Task B"}},
                "edges": [("task_1", "task_2")],
            }

    agent = ExecutiveAgent("meta")
    agent.mission_planner = StubPlanner()
    # use temporary session manager for isolation
    from jarvis.persistence.session import SessionManager

    agent.session_manager = SessionManager(base_dir=str(tmp_path))
    result = agent.manage_directive("Goal", session_id="sess1")
    assert result["success"] is True
    graph = result["graph"]
    assert graph["edges"] == [("task_1", "task_2")]
    saved = (tmp_path / "sess1" / "mission.json").read_text()
    data = json.loads(saved)
    assert data["tasks"] == ["Task A", "Task B"]
