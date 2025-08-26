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

world_pkg = types.ModuleType("jarvis.world_model")
predictive_mod = types.ModuleType("jarvis.world_model.predictive_simulation")

class _StubPredictor:
    def rank_actions(self, state, actions):
        return actions

predictive_mod.PredictiveSimulator = _StubPredictor
world_pkg.predictive_simulation = predictive_mod
jarvis_pkg.world_model = world_pkg
sys.modules["jarvis.world_model"] = world_pkg
sys.modules["jarvis.world_model.predictive_simulation"] = predictive_mod

memory_pkg = types.ModuleType("jarvis.memory")

class _DummyMemoryManager:
    pass


class _DummyProjectMemory:
    pass

memory_pkg.MemoryManager = _DummyMemoryManager
memory_pkg.ProjectMemory = _DummyProjectMemory
jarvis_pkg.memory = memory_pkg
sys.modules["jarvis.memory"] = memory_pkg

spec = importlib.util.spec_from_file_location(
    "jarvis.agents.mission_planner", ROOT / "jarvis" / "agents" / "mission_planner.py"
)
mission_planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mission_planner)
sys.modules["jarvis.agents.mission_planner"] = mission_planner
agents_pkg = types.ModuleType("jarvis.agents")
agents_pkg.mission_planner = mission_planner

# Use the critic stub from main
critics_mod = types.ModuleType("jarvis.agents.critics.ctde_critic")
class _DummyCritic:
    def __init__(self, *args, **kwargs):
        pass
    def review(self, *args, **kwargs):
        return {}
critics_mod.CTDECritic = _DummyCritic
agents_pkg = sys.modules.get("jarvis.agents", types.ModuleType("jarvis.agents"))
agents_pkg.critics = types.ModuleType("jarvis.agents.critics")
agents_pkg.critics.ctde_critic = critics_mod
sys.modules["jarvis.agents"] = agents_pkg
sys.modules["jarvis.agents.critics"] = agents_pkg.critics
sys.modules["jarvis.agents.critics.ctde_critic"] = critics_mod
