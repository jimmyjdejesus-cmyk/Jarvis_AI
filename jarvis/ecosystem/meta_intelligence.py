"""Meta-intelligence layer coordinating mission planning and execution.

Exposes :class:`ExecutiveAgent` which plans high level goals into mission DAGs
and executes them through an underlying orchestrator. Sub-orchestrators are
spawned automatically for team-scoped mission steps.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from jarvis.agents.base import AIAgent
from jarvis.agents.mission_planner import MissionPlanner
from jarvis.memory.project_memory import MemoryManager
from jarvis.orchestration.mission import Mission, MissionDAG
from jarvis.orchestration.orchestrator import MultiAgentOrchestrator
from jarvis.workflows.engine import (
    WorkflowEngine,
    WorkflowStatus,
    from_mission_dag,
)

try:  # pragma: no cover - neo4j is optional
    from jarvis.world_model.neo4j_graph import Neo4jGraph  # type: ignore
except Exception:  # pragma: no cover
    Neo4jGraph = None  # type: ignore


logger = logging.getLogger(__name__)

# Shared workflow engine instance used by tests
workflow_engine = WorkflowEngine()


class ExecutiveAgent(AIAgent):
    """High level agent responsible for mission planning and execution."""

    def __init__(
        self,
        name: str,
        *,
        mcp_client: Any | None = None,
        orchestrator_cls: type[MultiAgentOrchestrator] = MultiAgentOrchestrator,
        mission_planner: MissionPlanner | None = None,
        memory_manager: MemoryManager | None = None,
        knowledge_graph: Any | None = None,
    ) -> None:
        super().__init__(name, capabilities=[])
        self.mcp_client = mcp_client
        self.mission_planner = mission_planner or MissionPlanner()
        self.orchestrator = orchestrator_cls(
            self.mcp_client,
            knowledge_graph=knowledge_graph,
            memory=memory_manager,
        )
        try:  # pragma: no cover - optional dependency
            self.neo4j_graph = Neo4jGraph() if Neo4jGraph else None
        except Exception:  # pragma: no cover
            self.neo4j_graph = None

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------
    def plan(self, goal: str, context: Dict[str, Any]) -> MissionDAG:
        """Plan a mission for ``goal`` using the configured planner."""
        dag = self.mission_planner.plan(goal, context)
        self._spawn_sub_orchestrators(dag)
        return dag

    def _spawn_sub_orchestrators(self, dag: MissionDAG) -> None:
        """Create sub-orchestrators for each team scope in ``dag``.

        Each spawned child orchestrator is restricted to the specialists
        referenced by mission nodes within that team scope.
        """
        scope_specialists: Dict[str, set[str]] = {}
        for node in dag.nodes.values():
            if node.team_scope:
                scope_specialists.setdefault(node.team_scope, set()).add(
                    node.team_scope
                )

        for scope, specialists in scope_specialists.items():
            if (
                scope
                and scope not in self.orchestrator.specialists
                and scope not in self.orchestrator.child_orchestrators
            ):
                self.orchestrator.create_child_orchestrator(
                    scope,
                    {
                        "mission_name": scope,
                        "allowed_specialists": sorted(specialists),
                    },
                )

    # ------------------------------------------------------------------
    # Directive management and execution
    # ------------------------------------------------------------------
    def manage_directive(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mission plan for ``goal``.

        Returns a dictionary with ``success`` flag, list of ``tasks`` and the
        serialized mission graph under ``graph``. Errors are reported under
        ``critique``.
        """
        try:
            dag = self.plan(goal, context)
            tasks = [n.details or n.capability for n in dag.nodes.values()]
            return {"success": True, "tasks": tasks, "graph": dag.to_dict()}
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Mission planning failed")
            return {"success": False, "critique": {"message": str(exc)}}

    async def execute_mission(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan and execute a mission for ``goal``."""
        directive = self.manage_directive(goal, context)
        if not directive.get("success"):
            msg = directive.get("critique", {}).get("message", "")
            return {"success": False, "error": f"Mission planning failed: {msg}"}

        dag = MissionDAG.from_dict(directive["graph"])

        workflow = from_mission_dag(dag)
        completed = await workflow_engine.execute_workflow(workflow)

        ctx_results = getattr(completed.context, "results", {})
        if isinstance(ctx_results, dict):
            outputs = {k: v.output for k, v in ctx_results.items()}
            wm_results = [
                {
                    "step_id": k,
                    "success": v.status == WorkflowStatus.COMPLETED,
                    "facts": getattr(v, "facts", []),
                    "relationships": getattr(v, "relationships", []),
                }
                for k, v in ctx_results.items()
            ]
        else:  # pragma: no cover - defensive
            outputs = {}
            wm_results = []

        return {"success": True, "outputs": outputs, "world_model": wm_results}

