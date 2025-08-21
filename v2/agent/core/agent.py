"""LangGraph Agent Core Module - V2 Architecture.

This module provides a minimal yet functional agent that utilises the
`langgraph` package to build and execute a small workflow.  The goal is not to
be feature complete but to demonstrate how the new architecture wires together
workflow nodes, safety checks and streaming hooks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from langgraph.graph import END, StateGraph


class JarvisAgentV2:
    """Advanced agent using LangGraph architecture for enhanced reasoning."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, models=None, tools=None):
        """Initialize the V2 agent with LangGraph integration.

        Parameters
        ----------
        config:
            Optional configuration dictionary.  ``max_iterations`` may be
            provided to guard against runaway workflows.
        models:
            Mapping of model names to model instances.
        tools:
            Collection of tools available to the agent.
        """

        self.config = config or {}
        self.models = models or {}
        self.tools = tools or []

        # ``max_iterations`` prevents infinite loops when streaming results
        self.max_iterations: int = self.config.get("max_iterations", 25)

        # Workflow related attributes are initialised lazily
        self.workflow = None
        self.visualizer = None

        # External callback used for streaming events
        self._stream_hook: Optional[Callable[[Dict[str, Any]], None]] = None

    # ------------------------------------------------------------------
    def _emit_ws_event(self, node: str, data: Dict[str, Any]) -> None:
        """Emit an event using the lightweight WS7 schema.

        The WS7 schema used throughout the project is a simple dictionary with
        the following fields::

            {
                "type": "workflow.step",
                "node": "planner",
                "timestamp": "2025-01-01T12:00:00Z",
                "data": {...}
            }

        Parameters
        ----------
        node:
            Name of the workflow node that produced the event.
        data:
            Arbitrary payload emitted by the node.
        """

        event = {
            "type": "workflow.step",
            "node": node,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        # When a streaming hook is registered the event is forwarded to it so
        # that callers can observe workflow progress in real time.
        if self._stream_hook:
            try:
                self._stream_hook(event)
            except Exception:
                # Streaming callbacks should never break workflow execution
                pass

    # ------------------------------------------------------------------
    def setup_workflow(self) -> None:
        """Build the LangGraph workflow with nodes and edges.

        The workflow consists of three trivial nodes – ``planner``, ``executor``
        and ``critic`` – wired together in a straight line.  Each node emits a
        WS7 event when executed.
        """

        graph = StateGraph(dict)

        # ------------------------------------------------------------------
        def planner(state: Dict[str, Any]) -> Dict[str, Any]:
            plan = {"plan": f"Plan for: {state.get('query')}"}
            self._emit_ws_event("planner", plan)
            state.update(plan)
            return state

        def executor(state: Dict[str, Any]) -> Dict[str, Any]:
            result = {"execution": f"Executed plan: {state.get('plan')}"}
            self._emit_ws_event("executor", result)
            state.update(result)
            return state

        def critic(state: Dict[str, Any]) -> Dict[str, Any]:
            feedback = {"feedback": f"Reviewed: {state.get('execution')}"}
            self._emit_ws_event("critic", feedback)
            state.update(feedback)
            return state

        # Register nodes with the graph
        graph.add_node("planner", planner)
        graph.add_node("executor", executor)
        graph.add_node("critic", critic)

        # Configure entry point and edges
        graph.set_entry_point("planner")
        graph.add_edge("planner", "executor")
        graph.add_edge("executor", "critic")
        graph.add_edge("critic", END)

        # Compile into a runnable workflow
        self.workflow = graph.compile()

    # ------------------------------------------------------------------
    def run_workflow(
        self,
        query: str,
        stream_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Execute the agent workflow with optional streaming.

        Parameters
        ----------
        query:
            User request to process.
        stream_callback:
            Optional callable invoked for every WS7 event produced by the
            workflow.  When provided, the callback receives the event dictionary.
        """

        if self.workflow is None:
            self.setup_workflow()

        # Register streaming hook
        self._stream_hook = stream_callback

        state: Dict[str, Any] = {"query": query}
        final_state: Dict[str, Any] = state
        iterations = 0

        # ``stream`` yields the state after each node executes.  We forward
        # events to the hook and respect ``max_iterations`` to avoid infinite
        # loops during execution.
        for update in self.workflow.stream(state):
            for _node, data in update.items():
                final_state = data
                iterations += 1
                if iterations >= self.max_iterations:
                    return final_state

        return final_state

