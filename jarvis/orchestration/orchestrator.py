"""Reusable orchestration templates.

This module provides two lightweight orchestration helpers used throughout the
test-suite:

``MultiAgentOrchestrator``
    Coordinates a dictionary of specialist agents and records the reasoning
    path of each run.  It exposes a small API focused on the needs of the unit
    tests – coordinating specialists, tracking path memory and managing child
    orchestrators.

``DynamicOrchestrator``
    Builds LangGraph workflows from simple ``AgentSpec`` definitions.  It is a
    minimal wrapper that compiles an execution graph at runtime allowing tests
    to define arbitrary workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional
import logging

from langgraph.graph import StateGraph, END

from .path_memory import PathMemory

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Multi agent orchestration
# ---------------------------------------------------------------------------


class MultiAgentOrchestrator:
    """Coordinate a collection of specialist agents.

    Parameters
    ----------
    mcp_client:
        Client used by specialists.  Only stored for completeness – the
        orchestrator itself does not interact with it directly in the tests.
    specialists:
        Optional mapping of specialist name to the object implementing
        ``process_task``.
    """

    def __init__(
        self,
        mcp_client: Any,
        monitor: Any | None = None,
        knowledge_graph: Any | None = None,
        specialists: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.mcp_client = mcp_client
        self.monitor = monitor
        self.knowledge_graph = knowledge_graph
        self.specialists: Dict[str, Any] = specialists or {}
        self.child_orchestrators: Dict[str, "SubOrchestrator"] = {}

    # ------------------------------------------------------------------
    async def coordinate_specialists(
        self,
        request: str,
        code: str | None = None,
        user_context: str | None = None,
        novelty_boost: float = 0.0,
    ) -> Dict[str, Any]:
        """Run the available specialists on the request.

        The method tracks reasoning paths using :class:`PathMemory` and avoids
        executing previously failed paths unless a ``novelty_boost`` is
        supplied.
        """

        path_memory = PathMemory()
        avoid, similarity = path_memory.should_avoid(override=novelty_boost > 0)
        if avoid:
            return {
                "type": "error",
                "coordination_summary": f"Previously failed path (similarity {similarity:.2f})",
            }

        results: List[Dict[str, Any]] = []
        specialists_used: List[str] = []
        for name, specialist in self.specialists.items():
            path_memory.add_step(name)
            specialists_used.append(name)
            res = await specialist.process_task(request, context=code, user_context=user_context)
            results.append(res)

        score = (
            sum(r.get("confidence", 0.0) for r in results) / len(results)
            if results
            else 0.0
        )
        path_memory.record(score)

        return {
            "type": "single_specialist" if len(specialists_used) == 1 else "multi_specialist",
            "specialists_used": specialists_used,
            "results": results,
            "coordination_summary": "Completed",
        }

    # ------------------------------------------------------------------
    def create_child_orchestrator(self, name: str, spec: Dict[str, Any]):
        """Create and register a child :class:`SubOrchestrator`."""

        from .sub_orchestrator import SubOrchestrator  # Local import to avoid cycle

        child = SubOrchestrator(self.mcp_client, **spec)
        self.child_orchestrators[name] = child
        return child

    def list_child_orchestrators(self) -> List[str]:
        """Return identifiers of registered child orchestrators."""

        return list(self.child_orchestrators.keys())

    def remove_child_orchestrator(self, name: str) -> bool:
        """Remove a child orchestrator by name."""

        return self.child_orchestrators.pop(name, None) is not None


# ---------------------------------------------------------------------------
# Dynamic execution graphs
# ---------------------------------------------------------------------------


AgentCallable = Callable[[Dict[str, Any]], Dict[str, Any] | Awaitable[Dict[str, Any]]]


@dataclass
class AgentSpec:
    """Specification for a single node in the workflow."""

    name: str
    fn: AgentCallable
    next: Optional[str] = None
    condition: Optional[Callable[[Dict[str, Any]], str]] = None
    branches: Optional[Dict[str, Any]] = None
    entry: bool = False


class DynamicOrchestrator:
    """Compile and run LangGraph workflows from ``AgentSpec`` objects."""

    def __init__(self, agent_specs: List[AgentSpec]):
        self.agent_specs = agent_specs

        graph = StateGraph(dict)
        for spec in agent_specs:
            graph.add_node(spec.name, spec.fn)

        entry = next((s.name for s in agent_specs if s.entry), agent_specs[0].name)
        graph.set_entry_point(entry)

        for spec in agent_specs:
            if spec.next:
                graph.add_edge(spec.name, spec.next)
            if spec.condition and spec.branches:
                graph.add_conditional_edges(spec.name, spec.condition, spec.branches)

        self.workflow = graph.compile()

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the compiled workflow and return the final state."""

        logger.debug("Starting workflow with state: %s", state)
        result = await self.workflow.ainvoke(state)
        logger.debug("Workflow completed with state: %s", result)
        return result


__all__ = ["AgentSpec", "DynamicOrchestrator", "MultiAgentOrchestrator", "END"]

