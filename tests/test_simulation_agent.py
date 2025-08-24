import asyncio
import os
import sys

sys.path.append(os.getcwd())

from jarvis.agents import SimulationAgent
from jarvis.world_model.hypergraph import HierarchicalHypergraph


class DummyMCPClient:
    """Stub MCP client that records the last prompt."""

    def __init__(self) -> None:
        self.last_prompt = None

    async def generate_response(self, prompt: str) -> str:
        self.last_prompt = prompt
        return "Narrative"


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

