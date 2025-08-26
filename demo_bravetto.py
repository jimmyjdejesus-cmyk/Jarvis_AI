"""Demonstration script for the counterfactual Napoleon simulation."""

import asyncio
from jarvis.world_model.hypergraph import HierarchicalHypergraph
from jarvis.agents.simulation_agent import SimulationAgent
from jarvis.mcp.client import MCPClient


class ExecutiveAgent:  # pragma: no cover - demo stub
    """Minimal executive agent holding a hypergraph reference."""

    def __init__(self, mcp_client: MCPClient, hypergraph: HierarchicalHypergraph) -> None:
        self.mcp_client = mcp_client
        self.hypergraph = hypergraph


class DemoMCPClient(MCPClient):  # pragma: no cover - demo stub
    """Stub MCP client returning a fixed narrative."""

    async def generate_response(self, prompt: str) -> str:
        return (
            "Napoleon secures a decisive victory at Waterloo, reshaping Europe under "
            "French dominance."
        )


async def run_napoleon_test(
    executive_agent: ExecutiveAgent, simulation_agent: SimulationAgent
) -> None:
    """Run the Napoleon counterfactual simulation and print trace output."""

    print("\n--- DEMO 3: THE NAPOLEON TEST (3-LAYER TRACE) ---")
    query = "What would have happened if Napoleon won at Waterloo?"
    print(f"QUERY: \"{query}\"")

    # 1. Layer 3 Query (Intent)
    print("Querying Layer 3: Causal Graph to find the pivotal event...")
    causal_event_node = "battle_of_waterloo"
    causal_event_data = executive_agent.hypergraph.query(3, causal_event_node)
    print(
        f"Executive identifies pivotal event '{causal_event_node}' with known outcome: '{causal_event_data['outcome']}'"
    )

    # 2. Layer 2 Query (Strategy)
    print(
        "Querying Layer 2: Abstract Graph to retrieve the 'Counterfactual Simulation' strategy..."
    )
    strategy_node = "counterfactual_simulation"
    strategy_data = executive_agent.hypergraph.query(2, strategy_node)
    print(
        f"Executive retrieves the '{strategy_data['type']}' strategy: {strategy_data['steps']}"
    )

    # 3. Layer 1 Query & Simulation (Execution)
    print(
        "Querying Layer 1: Concrete Graph for ground truth data, then executing simulation..."
    )
    concrete_facts = executive_agent.hypergraph.layers[1]
    print(
        f"Simulation Agent will be grounded with concrete facts: {list(concrete_facts.keys())}"
    )

    intervention = {"node": causal_event_node, "new_outcome": "victory"}
    alternate_timeline = await simulation_agent.run_counterfactual(
        concrete_facts, causal_event_data, intervention
    )

    print("\n--- GENERATED COUNTERFACTUAL TIMELINE ---")
    print(alternate_timeline)


async def main() -> None:  # pragma: no cover - manual execution
    mcp_client = DemoMCPClient()
    hypergraph = HierarchicalHypergraph()
    hypergraph.load_from_json("jarvis/world_model/datasets/napoleon_waterloo.json")
    executive_agent = ExecutiveAgent(mcp_client, hypergraph)
    simulation_agent = SimulationAgent(mcp_client=mcp_client)

    await run_napoleon_test(executive_agent, simulation_agent)


if __name__ == "__main__":  # pragma: no cover - manual demonstration
    asyncio.run(main())
