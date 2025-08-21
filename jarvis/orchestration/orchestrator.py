"""Orchestration Template
==========================

This module provides a light‑weight orchestration engine that builds
LangGraph workflows dynamically from simple agent specifications.  The
previous implementation contained a large, hand crafted orchestrator for a
fixed set of specialist agents.  For testing and experimentation we now use a
generic approach where each mission supplies a list of agent specs describing
nodes and edges of an execution graph.

The orchestrator focuses on three core ideas:

* **Dynamic graph construction** – Nodes are created at runtime based on the
  provided specification.  Edges can be linear or conditional allowing for
  branching, looping and early termination.
* **LangGraph integration** – `StateGraph` from the `langgraph` package is
  used to compile a workflow that can be executed asynchronously.
* **Minimal interface** – Only a small API is required for the tests.  The
  orchestrator accepts agent specifications and exposes a ``run`` coroutine
  which executes the compiled workflow and returns the final state.

The intent of this module is to act as a reusable template that higher level
systems (such as the ``MetaAgent``) can delegate to when constructing
mission‑specific workflows.
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional

from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Agent specification model
# ---------------------------------------------------------------------------


AgentCallable = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class AgentSpec:
    """Specification for a single node in the workflow.

    Attributes
    ----------
    name:
        Identifier used inside the graph.
    fn:
        Callable executed when the node runs.  The callable receives and must
        return the workflow state (a mutable ``dict``).
    next:
        Optional name of the next node for a simple linear transition.
    condition:
        Optional callable returning a key from ``branches``.  When provided the
        orchestrator will create conditional edges using the mapping supplied
        in ``branches``.
    branches:
        Mapping of condition outputs to the name of the next node or ``END`` to
        finish the workflow.
    entry:
        Whether this node should be used as the entry point for the workflow.
    """

    name: str
    fn: AgentCallable
    next: Optional[str] = None
    condition: Optional[Callable[[Dict[str, Any]], str]] = None
    branches: Optional[Dict[str, Any]] = None
    entry: bool = False


# ---------------------------------------------------------------------------
# Dynamic orchestrator
# ---------------------------------------------------------------------------


class DynamicOrchestrator:
    """Build and execute LangGraph workflows from :class:`AgentSpec` objects."""

    def __init__(self, agent_specs: List[AgentSpec]):
        self.agent_specs = agent_specs

        # Build the StateGraph from the provided specifications
        graph = StateGraph(dict)

        for spec in agent_specs:
            graph.add_node(spec.name, spec.fn)

        # Determine entry point – default to the first spec if none marked
        entry = next((s.name for s in agent_specs if s.entry), agent_specs[0].name)
        graph.set_entry_point(entry)

        # Wire up edges
        for spec in agent_specs:
            if spec.next:
                graph.add_edge(spec.name, spec.next)

            if spec.condition and spec.branches:
                graph.add_conditional_edges(spec.name, spec.condition, spec.branches)

        # Compile to a runnable workflow
        self.workflow = graph.compile()

    # ------------------------------------------------------------------
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the compiled workflow.

        Parameters
        ----------
        state:
            Initial state passed to the workflow.  The state is mutated by
            nodes in the graph.  The final state after execution is returned.
        """

        logger.debug("Starting workflow with state: %s", state)
        result = await self.workflow.ainvoke(state)
        logger.debug("Workflow completed with state: %s", result)
        return result


# For backward compatibility some parts of the codebase still import
# ``MultiAgentOrchestrator``.  Exporting the new class under this name keeps the
# surface area stable while the internals have been simplified.
class MultiAgentOrchestrator(DynamicOrchestrator):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "MultiAgentOrchestrator is deprecated and will be removed in a future release. "
            "Please use DynamicOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

__all__ = ["AgentSpec", "DynamicOrchestrator", "MultiAgentOrchestrator", "END"]

