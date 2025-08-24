import asyncio
import os
import sys
import importlib.util
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(os.getcwd())

agents_pkg = types.ModuleType("jarvis.agents")
sys.modules["jarvis.agents"] = agents_pkg

bs_spec = importlib.util.spec_from_file_location(
    "jarvis.agents.base_specialist", ROOT / "jarvis" / "agents" / "base_specialist.py"
)
base_specialist_mod = importlib.util.module_from_spec(bs_spec)
bs_spec.loader.exec_module(base_specialist_mod)
agents_pkg.base_specialist = base_specialist_mod
sys.modules["jarvis.agents.base_specialist"] = base_specialist_mod

sim_spec = importlib.util.spec_from_file_location(
    "jarvis.agents.simulation_agent", ROOT / "jarvis" / "agents" / "simulation_agent.py"
)
simulation_agent = importlib.util.module_from_spec(sim_spec)
sim_spec.loader.exec_module(simulation_agent)
sys.modules["jarvis.agents.simulation_agent"] = simulation_agent
SimulationAgent = simulation_agent.SimulationAgent

hg_spec = importlib.util.spec_from_file_location(
    "jarvis.world_model.hypergraph", ROOT / "jarvis" / "world_model" / "hypergraph.py"
)
hypergraph_mod = importlib.util.module_from_spec(hg_spec)
hg_spec.loader.exec_module(hypergraph_mod)
sys.modules["jarvis.world_model.hypergraph"] = hypergraph_mod
HierarchicalHypergraph = hypergraph_mod.HierarchicalHypergraph


class DummyMCPClient:
    """Stub MCP client that records the last prompt."""

    def __init__(self) -> None:
        self.last_prompt = None

    async def generate_response(self, prompt: str) -> str:
        self.last_prompt = prompt
        return "Narrative"


class DummyPredictor:
    """Simple predictor with fixed evaluation score."""

    def evaluate(self, state, action):
        return 0.8


def test_simulation_agent_records_causal_belief() -> None:
    mcp = DummyMCPClient()
    hg = HierarchicalHypergraph()
    agent = SimulationAgent(mcp, hypergraph=hg)

    concrete = {"troops": "large"}
    causal_event = {"name": "battle_of_waterloo", "outcome": "defeat"}
    intervention = {"node": "battle_of_waterloo", "new_outcome": "victory"}

    narrative = asyncio.run(
        agent.run_counterfactual(concrete, causal_event, intervention, confidence=0.85)
    )

    assert mcp.last_prompt is not None
    assert "victory" in mcp.last_prompt
    assert causal_event["outcome"] == "defeat"  # original dict remains unchanged
    assert narrative == "Narrative"
    belief = hg.query(3, "battle_of_waterloo->victory")
    assert belief is not None and belief["confidence"] == 0.85


def test_quick_simulate_blends_scores() -> None:
    class DummyLLM(DummyMCPClient):
        async def generate_response(self, prompt: str) -> str:
            return "0.4"

    agent = SimulationAgent(DummyLLM(), simulator=DummyPredictor())
    score = asyncio.run(agent.quick_simulate({"value": 0}, "move"))
    assert abs(score - 0.6) < 1e-6

