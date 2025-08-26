import pytest
import sys
from pathlib import Path
from typing import List

# Ensure the project root is in the path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from jarvis.planning.mcts_planner import MCTSPlanner

# --- Test Fixtures ---

AVAILABLE_TOOLS = ["search_web", "read_file", "write_file", "summarize"]

class DummyMCPClient:
    """A mock client that deterministically rates toolchains."""
    async def generate_response(self, server: str, model: str, prompt: str) -> str:
        # A good plan involves searching then writing.
        if "search_web" in prompt and "write_file" in prompt:
            return "9"
        # A mediocre plan is just searching.
        if "search_web" in prompt:
            return "6"
        # A bad plan is writing without reading first.
        if "write_file" in prompt and "read_file" not in prompt:
            return "2"
        # Any other combination is just okay.
        return "5"

@pytest.fixture
def mcts_planner():
    """Returns an MCTSPlanner instance with a dummy client and tools."""
    client = DummyMCPClient()
    return MCTSPlanner(
        mcp_client=client,
        available_tools=AVAILABLE_TOOLS,
        iterations=50,  # Lower iterations for faster tests
        exploration_weight=1.5,
    )

# --- Tests ---

@pytest.mark.asyncio
async def test_planner_initialization(mcts_planner: MCTSPlanner):
    """Test that the MCTSPlanner initializes correctly."""
    assert mcts_planner.mcp_client is not None
    assert mcts_planner.available_tools == AVAILABLE_TOOLS
    assert mcts_planner.iterations == 50

@pytest.mark.asyncio
async def test_find_best_toolchain_selects_optimal_path(mcts_planner: MCTSPlanner):
    """
    Tests that the planner explores and selects the toolchain
    that the dummy client is designed to rate most highly.
    """
    goal = "Research the latest AI trends and write a report."

    best_toolchain = await mcts_planner.find_best_toolchain(goal)

    # The dummy client gives the highest reward to toolchains with both search and write.
    # The exact path might vary, but the best path should contain these two.
    assert "search_web" in best_toolchain
    assert "write_file" in best_toolchain

    # It should also be a valid sequence of tools.
    assert isinstance(best_toolchain, list)
    for tool in best_toolchain:
        assert tool in AVAILABLE_TOOLS

@pytest.mark.asyncio
async def test_empty_plan_for_no_tools():
    """Test that the planner returns an empty list if no tools are available."""
    client = DummyMCPClient()
    planner = MCTSPlanner(client, available_tools=[], iterations=10)

    best_toolchain = await planner.find_best_toolchain("Any goal")

    assert best_toolchain == []
