"""Agent bridge between legacy orchestration and the new AgentManager.

This module provides a compatibility layer so existing legacy workflows and
entrypoints can execute tasks using the new agent runtime without large-scale
refactors. It exposes a high-level API to execute single-agent tasks,
multi-agent collaborations, and to introspect agent capabilities.

Security model: This bridge does not grant elevated permissions by itself.
Callers are expected to apply security validation upstream (see security_bridge).
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LegacyAgentTask:
    """Legacy-compatible agent task envelope.

    Attributes:
        task_id: Unique identifier for the task.
        agent_type: Logical agent type (e.g. "research", "coding").
        objective: Human-readable objective or prompt for the task.
        context: Optional structured context to pass to the agent.
        priority: Relative priority for scheduling.
        timeout: Soft timeout in seconds for the task to complete.
    """

    task_id: str
    agent_type: str
    objective: str
    context: Dict[str, Any]
    priority: int = 1
    timeout: int = 300


class AgentBridge:
    """Bridge between the new AgentManager and legacy orchestration.

    This class adapts legacy task shapes and agent type names to the new agent
    system so that older orchestrators and workflows can schedule work without
    migrating their internal formats.
    """

    def __init__(self, new_agent_manager=None, new_ollama_client=None):
        """Initialize the bridge.

        Args:
            new_agent_manager: Instance of the new AgentManager.
            new_ollama_client: Instance of the new OllamaClient for LLM calls.
        """
        self.new_agent_manager = new_agent_manager
        self.new_ollama_client = new_ollama_client
        self.agent_type_mapping = {
            "research": "research_agent",
            "coding": "coding_agent",
            "curiosity": "curiosity_agent",
            "benchmark": "benchmark_agent",
            "default": "default_agent",
        }

    async def execute_legacy_task(self, task: LegacyAgentTask) -> Dict[str, Any]:
        """Execute a legacy task using the new agent system.

        Args:
            task: The legacy task envelope to execute.

        Returns:
            A dictionary containing the execution result with fields
            like result, success, duration, and error if present.
        """
        if not self.new_agent_manager:
            return {"error": "New agent manager not available"}

        try:
            agent_id = self.agent_type_mapping.get(task.agent_type, "default_agent")

            if agent_id not in self.new_agent_manager.agents:
                await self._ensure_agent_exists(agent_id, task.agent_type)

            result = await self.new_agent_manager.execute_task(
                agent_id=agent_id,
                task_type="legacy_execution",
                prompt=task.objective,
                context=task.context,
                timeout=task.timeout,
            )

            return {
                "task_id": task.task_id,
                "agent_id": agent_id,
                "result": result.result if hasattr(result, "result") else str(result),
                "success": not result.is_failed if hasattr(result, "is_failed") else True,
                "duration": result.duration if hasattr(result, "duration") else None,
                "error": result.error if hasattr(result, "error") else None,
            }

        except Exception as e:
            logger.error(f"Failed to execute legacy task {task.task_id}: {e}")
            return {"task_id": task.task_id, "error": str(e), "success": False}

    async def _ensure_agent_exists(self, agent_id: str, agent_type: str):
        """Ensure that a mapped agent exists in the new manager, creating it if needed.

        This will instantiate and register a best-match agent class for the
        provided logical agent type.
        """
        try:
            from jarvis.agents.research_agent import ResearchAgent
            from jarvis.agents.coding_agent import CodingAgent
            from jarvis.agents.curiosity_agent import CuriosityAgent
            from jarvis.agents.benchmark_agent import BenchmarkAgent
            from jarvis.agents.base import BaseAgent

            agent_classes = {
                "research_agent": ResearchAgent,
                "coding_agent": CodingAgent,
                "curiosity_agent": CuriosityAgent,
                "benchmark_agent": BenchmarkAgent,
                "default_agent": BaseAgent,
            }

            agent_class = agent_classes.get(agent_id, BaseAgent)
            agent = agent_class(agent_id=agent_id)
            self.new_agent_manager.register_agent(agent)
            logger.info(f"Created and registered agent {agent_id}")

        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            raise

    async def get_agent_capabilities(self, agent_type: str) -> Dict[str, Any]:
        """Return capabilities and status metadata for a logical agent type.

        Args:
            agent_type: Logical agent type, e.g. "research".

        Returns:
            A dictionary describing capabilities and current status.
        """
        agent_id = self.agent_type_mapping.get(agent_type, "default_agent")

        if not self.new_agent_manager or agent_id not in self.new_agent_manager.agents:
            return {"error": "Agent not available"}

        agent = self.new_agent_manager.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}

        return {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "capabilities": getattr(agent, "capabilities", []),
            "status": self.new_agent_manager.get_agent_status(agent_id).value if self.new_agent_manager.get_agent_status(agent_id) else "unknown",
        }

    async def list_available_agents(self) -> List[Dict[str, Any]]:
        """List all currently registered agents with status and capabilities."""
        if not self.new_agent_manager:
            return []

        agents = []
        for agent_id, agent in self.new_agent_manager.agents.items():
            legacy_type = None
            for lt, nt in self.agent_type_mapping.items():
                if nt == agent_id:
                    legacy_type = lt
                    break

            agents.append(
                {
                    "agent_id": agent_id,
                    "legacy_type": legacy_type or "unknown",
                    "status": self.new_agent_manager.get_agent_status(agent_id).value if self.new_agent_manager.get_agent_status(agent_id) else "unknown",
                    "capabilities": getattr(agent, "capabilities", []),
                }
            )

        return agents

    async def execute_collaboration(self, agent_types: List[str], objective: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Execute a multi-agent collaboration with the specified logical agent types.

        Args:
            agent_types: Logical agent types to participate.
            objective: Shared objective for collaboration.
            context: Optional shared context passed to all agents.

        Returns:
            Collaboration result with per-agent outcomes and metadata.
        """
        if not self.new_agent_manager:
            return {"error": "New agent manager not available"}

        try:
            for agent_type in agent_types:
                agent_id = self.agent_type_mapping.get(agent_type, "default_agent")
                if agent_id not in self.new_agent_manager.agents:
                    await self._ensure_agent_exists(agent_id, agent_type)

            from jarvis.core.agent_manager import CollaborationRequest, CollaborationMode

            request = CollaborationRequest(
                request_id=f"legacy_collab_{asyncio.get_event_loop().time()}",
                initiator_id="legacy_system",
                target_agents=[self.agent_type_mapping.get(at, "default_agent") for at in agent_types],
                task_description=objective,
                mode=CollaborationMode.PARALLEL,
                context=context or {},
            )

            result_id = await self.new_agent_manager.initiate_collaboration(request)
            await asyncio.sleep(1)

            return {
                "collaboration_id": result_id,
                "agent_types": agent_types,
                "objective": objective,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Failed to execute collaboration: {e}")
            return {"error": str(e), "success": False}


# Global bridge instance
agent_bridge = None


def initialize_agent_bridge(new_agent_manager=None, new_ollama_client=None):
    """Initialize and register a global AgentBridge instance."""
    global agent_bridge
    agent_bridge = AgentBridge(new_agent_manager, new_ollama_client)
    return agent_bridge


def get_agent_bridge() -> Optional[AgentBridge]:
    """Return the global AgentBridge instance if initialized."""
    return agent_bridge
