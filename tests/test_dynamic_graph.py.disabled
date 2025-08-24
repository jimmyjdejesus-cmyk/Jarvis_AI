import pytest
import sys
from pathlib import Path

# Ensure repository root on path for direct test execution
sys.path.append(str(Path(__file__).resolve().parents[1]))

from jarvis.ecosystem.meta_intelligence import ExecutiveAgent
from jarvis.orchestration import END


@pytest.mark.asyncio
async def test_branching_execution():
    """MetaAgent should route execution based on conditional edges."""

    meta = ExecutiveAgent("meta")

    def start(state):
        state.setdefault("visited", []).append("start")
        return state

    def router(state):
        # no-op router, decision handled by condition function
        return state

    def choose_branch(state):
        return state.get("path", "a")

    def agent_a(state):
        state["visited"].append("a")
        return state

    def agent_b(state):
        state["visited"].append("b")
        return state

    specs = [
        {"name": "start", "fn": start, "next": "router", "entry": True},
        {
            "name": "router",
            "fn": router,
            "condition": choose_branch,
            "branches": {"a": "agent_a", "b": "agent_b"},
        },
        {"name": "agent_a", "fn": agent_a},
        {"name": "agent_b", "fn": agent_b},
    ]

    meta.create_execution_graph("mission", specs)

    state = {"path": "a"}
    result = await meta.delegate("mission", state)

    assert result["visited"] == ["start", "a"]


@pytest.mark.asyncio
async def test_looping_execution():
    """The orchestrator should support loops via conditional edges."""

    meta = ExecutiveAgent("meta")

    def increment(state):
        state["count"] = state.get("count", 0) + 1
        return state

    def check(state):
        # decision is handled by the condition function
        return state

    def should_continue(state):
        return "again" if state["count"] < 2 else "done"

    specs = [
        {"name": "increment", "fn": increment, "next": "check", "entry": True},
        {
            "name": "check",
            "fn": check,
            "condition": should_continue,
            "branches": {"again": "increment", "done": END},
        },
    ]

    meta.create_execution_graph("loop", specs)

    result = await meta.delegate("loop", {"count": 0})
    assert result["count"] == 2

