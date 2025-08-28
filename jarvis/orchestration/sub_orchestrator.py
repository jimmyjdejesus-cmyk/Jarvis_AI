"""Sub-orchestrator for scoped missions.

This class inherits from :class:`MultiAgentOrchestrator` but allows
restricting the available specialists to those relevant for a specific
sub-mission. It enables nested orchestration where each mission segment can
run with its own focused set of tools and agents.
"""
from typing import Dict, List, Optional, Any

from jarvis.homeostasis.monitor import SystemMonitor
from jarvis.memory.project_memory import ProjectMemory
try:  # pragma: no cover - optional dependency
    from jarvis.world_model.knowledge_graph import KnowledgeGraph
except Exception:  # pragma: no cover
    from typing import Any

    KnowledgeGraph = Any  # type: ignore
from .orchestrator import MultiAgentOrchestrator


class SubOrchestrator(MultiAgentOrchestrator):
    """Orchestrator tailored for a single sub-mission."""

    def __init__(
        self,
        mcp_client,
        mission_name: Optional[str] = None,
        allowed_specialists: Optional[List[str]] = None,
        custom_specialists: Optional[Dict[str, Any]] = None,
        child_specs: Optional[Dict[str, Dict[str, Any]]] = None,
        monitor: SystemMonitor | None = None,
        knowledge_graph: KnowledgeGraph | None = None,
        memory: ProjectMemory | None = None,
    ):
        """Create a new sub-orchestrator.

        Args:
            mcp_client: MCP client shared with the parent orchestrator.
            mission_name: Optional name for this sub-mission.
            allowed_specialists: Optional list restricting which specialists
                are available within this orchestrator.
            custom_specialists: Optional mapping of specialist name to a
                specialist instance. When provided, these replace the default
                specialist set. This is primarily useful for testing.
            child_specs: Optional mapping of nested sub-orchestrator
                specifications.
        """
        super().__init__(
            mcp_client,
            monitor=monitor,
            knowledge_graph=knowledge_graph,
            memory=memory,
        )
        self.mission_name = mission_name

        if child_specs:
            for name, spec in child_specs.items():
                self.create_child_orchestrator(name, spec)

        if custom_specialists is not None:
            self.specialists = {
                name: agent
                for name, agent in custom_specialists.items()
                if allowed_specialists is None or name in set(allowed_specialists)
            }
        elif allowed_specialists is not None:
            self.specialists = {
                name: agent
                for name, agent in self.specialists.items()
                if name in set(allowed_specialists)
            }

    async def run_mission_dag(self, dag, context: Any | None = None) -> Any:
        """Execute a :class:`~jarvis.orchestration.mission.MissionDAG` within this orchestrator.

        The DAG is converted to a workflow and executed using the shared
        workflow engine. Only specialists registered with this sub-orchestrator
        (or its children) will be available during execution. If the DAG
        references a specialist outside this set, execution is aborted.
        """
        from jarvis.workflows.engine import from_mission_dag, WorkflowEngine

        for node in dag.nodes.values():
            if (
                node.team_scope not in self.specialists
                and node.team_scope not in self.child_orchestrators
            ):
                raise ValueError(
                    f"Specialist '{node.team_scope}' not allowed in this sub-orchestrator"
                )

        workflow = from_mission_dag(dag)
        engine = WorkflowEngine()
        return await engine.execute_workflow(workflow)
