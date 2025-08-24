"""Sub-orchestrator for scoped missions.

This class inherits from :class:`MultiAgentOrchestrator` but allows
restricting the available specialists to those relevant for a specific
sub-mission. It enables nested orchestration where each mission segment can
run with its own focused set of tools and agents.
"""
from typing import Dict, List, Optional, Any

from jarvis.homeostasis.monitor import SystemMonitor
from jarvis.world_model.knowledge_graph import KnowledgeGraph
from .orchestrator import MultiAgentOrchestrator


class SubOrchestrator(MultiAgentOrchestrator):
    """Orchestrator tailored for a single sub-mission."""

    def __init__(
        self,
        mcp_client,
        mission_name: Optional[str] = None,
        allowed_specialists: Optional[List[str]] = None,
        custom_specialists: Optional[Dict[str, Any]] = None,
        monitor: SystemMonitor | None = None,
        knowledge_graph: KnowledgeGraph | None = None,
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
        """
        super().__init__(mcp_client, monitor=monitor, knowledge_graph=knowledge_graph)
        self.mission_name = mission_name

        if custom_specialists is not None:
            self.specialists = custom_specialists
        elif allowed_specialists is not None:
            self.specialists = {
                name: agent
                for name, agent in self.specialists.items()
                if name in set(allowed_specialists)
            }

