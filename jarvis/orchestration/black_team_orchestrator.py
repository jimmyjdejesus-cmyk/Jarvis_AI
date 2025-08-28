"""Standalone orchestrator for Black team missions.

This orchestrator focuses exclusively on running the
:class:`~jarvis.orchestration.team_agents.BlackInnovatorAgent`.
It accepts high level objectives and coordinates task execution
with simple context filtering.  Results are broadcast to a shared
:class:`~jarvis.memory.memory_bus.MemoryBus` when provided.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from jarvis.memory.memory_bus import MemoryBus
from .team_agents import BlackInnovatorAgent


class BlackTeamOrchestrator:
    """Coordinate Black team missions independently of other teams."""

    def __init__(
        self,
        objective: str,
        directory: str = ".",
        shared_bus: MemoryBus | None = None,
    ) -> None:
        self.objective = objective
        self.shared_bus = shared_bus
        self.memory_bus = MemoryBus(directory)
        self.shared_docs_bus = MemoryBus(os.path.join(directory, "shared_docs"))
        self.team_buses = {"Black": MemoryBus(os.path.join(directory, "black"))}
        self.team_status = {"Black": "running"}
        self.agent = BlackInnovatorAgent(self)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Return only context entries related to disruptive signals."""
        return {
            k: v
            for k, v in context.items()
            if "disrupt" in k.lower() or "disrupt" in str(v).lower()
        }

    def broadcast(self, message: str, data: Dict[str, Any] | None = None) -> None:
        """Broadcast a message to the shared bus if available."""
        if self.shared_bus:
            self.shared_bus.log_interaction(self.agent.agent_id, "Black", message, data)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_mission(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Execute a list of tasks using the BlackInnovatorAgent.

        Parameters
        ----------
        tasks:
            Each task dictionary may contain ``id``, ``description`` and
            optional ``context`` keys.
        context:
            Base context applied to every task prior to filtering.
        """
        results: List[Dict[str, Any]] = []
        base_ctx = context or {}
        for task in tasks:
            task_ctx = {**base_ctx, **task.get("context", {})}
            filtered = self._filter_context(task_ctx)
            objective = task.get("description", self.objective)
            output = self.agent.run(objective, filtered)
            results.append({"task_id": task.get("id"), "output": output})
            self.broadcast(f"Completed {objective}", output)
        return results


__all__ = ["BlackTeamOrchestrator"]
