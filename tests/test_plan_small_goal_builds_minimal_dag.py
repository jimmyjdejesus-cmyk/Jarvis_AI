import os
import sys
import types
import importlib.util
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

# Stub minimal jarvis environment to load mission planner
jarvis_pkg = types.ModuleType("jarvis")
sys.modules["jarvis"] = jarvis_pkg

models_pkg = types.ModuleType("jarvis.models")
client_mod = types.ModuleType("jarvis.models.client")
class _Client:
    def generate_response(self, model, prompt):
        return ""
client_mod.model_client = _Client()
models_pkg.client = client_mod
sys.modules["jarvis.models"] = models_pkg
sys.modules["jarvis.models.client"] = client_mod

world_pkg = types.ModuleType("jarvis.world_model")
predictive_mod = types.ModuleType("jarvis.world_model.predictive_simulation")
class _Pred:
    def rank_actions(self, state, actions):
        return actions
predictive_mod.PredictiveSimulator = _Pred
kg_mod = types.ModuleType("jarvis.world_model.knowledge_graph")
class _KG:
    def get_files(self):
        return ["file_a.py"]
kg_mod.KnowledgeGraph = _KG
world_pkg.predictive_simulation = predictive_mod
world_pkg.knowledge_graph = kg_mod
sys.modules["jarvis.world_model"] = world_pkg
sys.modules["jarvis.world_model.predictive_simulation"] = predictive_mod
sys.modules["jarvis.world_model.knowledge_graph"] = kg_mod

memory_pkg = types.ModuleType("jarvis.memory")
proj_mem_mod = types.ModuleType("jarvis.memory.project_memory")
class _MM:
    def add(self, *args, **kwargs):
        pass
    def query(self, *args, **kwargs):
        return [{"text": "remembered"}]
proj_mem_mod.MemoryManager = _MM
proj_mem_mod.ProjectMemory = None
memory_pkg.project_memory = proj_mem_mod
sys.modules["jarvis.memory"] = memory_pkg
sys.modules["jarvis.memory.project_memory"] = proj_mem_mod

spec_mission = importlib.util.spec_from_file_location(
    "jarvis.orchestration.mission", ROOT / "jarvis" / "orchestration" / "mission.py"
)
mission_module = importlib.util.module_from_spec(spec_mission)
sys.modules["jarvis.orchestration.mission"] = mission_module
spec_mission.loader.exec_module(mission_module)

spec_planner = importlib.util.spec_from_file_location(
    "jarvis.agents.mission_planner", ROOT / "jarvis" / "agents" / "mission_planner.py"
)
mission_planner = importlib.util.module_from_spec(spec_planner)
sys.modules["jarvis.agents.mission_planner"] = mission_planner
spec_planner.loader.exec_module(mission_planner)
MissionPlanner = mission_planner.MissionPlanner
BaseMemoryManager = mission_planner.MemoryManager


class DummyMemory(BaseMemoryManager):
    pass  # query implemented via stub


class DummyKG:
    def get_files(self) -> List[str]:
        return ["file_a.py"]


def test_plan_small_goal_builds_minimal_dag(tmp_path, monkeypatch):
    monkeypatch.setattr(mission_module, "MISSION_DIR", str(tmp_path))
    events: List[tuple[str, Dict[str, Any]]] = []

    def handler(name: str, payload: Dict[str, Any]) -> None:
        events.append((name, payload))

    planner = MissionPlanner(memory=DummyMemory(), knowledge_graph=DummyKG(), event_handler=handler)
    dag = planner.plan("do something", {"title": "t", "project": "p", "session": "s"})

    path = os.path.join(tmp_path, f"{dag.mission_id}.json")
    assert os.path.exists(path)
    assert "execute_goal" in dag.nodes
    assert events and events[0][0] == "Mission_Planned"
