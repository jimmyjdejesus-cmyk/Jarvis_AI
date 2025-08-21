import json

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
MetaAgent = meta_module.MetaAgent


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


def test_meta_agent_plan_mission_builds_graph(tmp_path):
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

    agent = MetaAgent("meta")
    agent.mission_planner = StubPlanner()
    # use temporary session manager for isolation
    from jarvis.persistence.session import SessionManager

    agent.session_manager = SessionManager(base_dir=str(tmp_path))
    graph = agent.plan_mission("Goal", session_id="sess1")
    assert graph["edges"] == [("task_1", "task_2")]
    saved = (tmp_path / "sess1" / "mission.json").read_text()
    data = json.loads(saved)
    assert data["tasks"] == ["Task A", "Task B"]
