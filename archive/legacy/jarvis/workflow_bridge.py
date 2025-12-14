"""Workflow bridge mapping legacy workflow intents to the new runtime.

Provides adapters to execute research, analysis, and benchmark workflows using
new AgentManager-based collaboration primitives. Also exposes capability and
status introspection helpers for orchestration UIs and API layers.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LegacyWorkflowTask:
    """Legacy workflow task envelope.

    Attributes:
        task_id: Unique identifier for this workflow request.
        workflow_type: One of {"research", "analysis", "benchmark"}.
        parameters: Workflow-specific parameters (e.g., query, max_results).
        priority: Relative priority for scheduling executions.
        timeout: Soft timeout in seconds for the workflow.
    """

    task_id: str
    workflow_type: str
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: int = 600


class WorkflowBridge:
    """Bridge between new workflow systems and legacy orchestration.

    Coordinates research/analysis/benchmark tasks via new collaboration APIs.
    """

    def __init__(self, new_agent_manager=None, new_knowledge_graph=None):
        """Initialize the workflow bridge.

        Args:
            new_agent_manager: AgentManager instance used to coordinate agents.
            new_knowledge_graph: KnowledgeGraph instance (optional) for context.
        """
        self.new_agent_manager = new_agent_manager
        self.new_knowledge_graph = new_knowledge_graph
        self.workflow_type_mapping = {
            "research": "research_pipeline",
            "analysis": "analysis_workflow",
            "collaboration": "agent_collaboration",
            "benchmark": "benchmark_workflow",
        }

    async def execute_research_workflow(self, task: LegacyWorkflowTask) -> Dict[str, Any]:
        """Execute a research workflow using the research pipeline.

        Args:
            task: LegacyWorkflowTask with parameters {query, max_results?, enable_web_search?}.

        Returns:
            A dictionary containing workflow status metadata.
        """
        if not self.new_agent_manager:
            return {"error": "New agent manager not available"}

        try:
            query = task.parameters.get("query", "")
            max_results = task.parameters.get("max_results", 50)
            enable_web_search = task.parameters.get("enable_web_search", True)

            from jarvis.core.agent_manager import CollaborationRequest, CollaborationMode

            request = CollaborationRequest(
                request_id=f"research_{task.task_id}",
                initiator_id="workflow_bridge",
                target_agents=["research_agent"],
                task_description=f"Research: {query}",
                mode=CollaborationMode.INDEPENDENT,
                context={
                    "query": query,
                    "max_results": max_results,
                    "enable_web_search": enable_web_search,
                    "workflow_type": "research",
                },
            )

            result_id = await self.new_agent_manager.initiate_collaboration(request)
            await asyncio.sleep(2)

            return {
                "task_id": task.task_id,
                "workflow_type": "research",
                "collaboration_id": result_id,
                "query": query,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Failed to execute research workflow {task.task_id}: {e}")
            return {"task_id": task.task_id, "error": str(e), "success": False}

    async def execute_analysis_workflow(self, task: LegacyWorkflowTask) -> Dict[str, Any]:
        """Execute an analysis workflow leveraging multiple agents.

        Args:
            task: LegacyWorkflowTask with parameters {data, analysis_type?}.

        Returns:
            A dictionary describing coordination status.
        """
        if not self.new_agent_manager:
            return {"error": "New agent manager not available"}

        try:
            data = task.parameters.get("data", "")
            analysis_type = task.parameters.get("analysis_type", "general")

            agent_types = ["coding_agent", "research_agent"]
            if analysis_type == "creative":
                agent_types.append("curiosity_agent")

            from jarvis.core.agent_manager import CollaborationRequest, CollaborationMode

            request = CollaborationRequest(
                request_id=f"analysis_{task.task_id}",
                initiator_id="workflow_bridge",
                target_agents=agent_types,
                task_description=f"Analyze: {data[:100]}...",
                mode=CollaborationMode.PARALLEL,
                context={"data": data, "analysis_type": analysis_type, "workflow_type": "analysis"},
            )

            result_id = await self.new_agent_manager.initiate_collaboration(request)

            return {
                "task_id": task.task_id,
                "workflow_type": "analysis",
                "collaboration_id": result_id,
                "analysis_type": analysis_type,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Failed to execute analysis workflow {task.task_id}: {e}")
            return {"task_id": task.task_id, "error": str(e), "success": False}

    async def execute_benchmark_workflow(self, task: LegacyWorkflowTask) -> Dict[str, Any]:
        """Execute a benchmark workflow using the benchmark agent.

        Args:
            task: LegacyWorkflowTask with parameters {test_suite?, agents?}.
        """
        if not self.new_agent_manager:
            return {"error": "New agent manager not available"}

        try:
            test_suite = task.parameters.get("test_suite", "default")
            agents_to_test = task.parameters.get("agents", ["research_agent", "coding_agent"])

            from jarvis.core.agent_manager import CollaborationRequest, CollaborationMode

            request = CollaborationRequest(
                request_id=f"benchmark_{task.task_id}",
                initiator_id="workflow_bridge",
                target_agents=["benchmark_agent"],
                task_description=f"Run benchmark: {test_suite}",
                mode=CollaborationMode.INDEPENDENT,
                context={"test_suite": test_suite, "agents_to_test": agents_to_test, "workflow_type": "benchmark"},
            )

            result_id = await self.new_agent_manager.initiate_collaboration(request)

            return {
                "task_id": task.task_id,
                "workflow_type": "benchmark",
                "collaboration_id": result_id,
                "test_suite": test_suite,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Failed to execute benchmark workflow {task.task_id}: {e}")
            return {"task_id": task.task_id, "error": str(e), "success": False}

    async def execute_workflow(self, task: LegacyWorkflowTask) -> Dict[str, Any]:
        """Dispatch a legacy workflow task to the appropriate execution path."""
        workflow_type = task.workflow_type.lower()
        if workflow_type == "research":
            return await self.execute_research_workflow(task)
        if workflow_type == "analysis":
            return await self.execute_analysis_workflow(task)
        if workflow_type == "benchmark":
            return await self.execute_benchmark_workflow(task)
        return {"task_id": task.task_id, "error": f"Unknown workflow type: {workflow_type}", "success": False}

    async def get_workflow_capabilities(self) -> Dict[str, Any]:
        """Return supported workflows with parameters and agent participation."""
        capabilities = {
            "research": {"description": "Research workflow using research pipeline", "parameters": ["query", "max_results", "enable_web_search"], "agents": ["research_agent"]},
            "analysis": {"description": "Analysis workflow using multiple agents", "parameters": ["data", "analysis_type"], "agents": ["coding_agent", "research_agent", "curiosity_agent"]},
            "benchmark": {"description": "Benchmark workflow using benchmark agent", "parameters": ["test_suite", "agents"], "agents": ["benchmark_agent"]},
            "collaboration": {"description": "Multi-agent collaboration workflow", "parameters": ["agents", "objective", "mode"], "agents": ["all"]},
        }
        return {"available_workflows": list(capabilities.keys()), "capabilities": capabilities, "bridge_available": self.new_agent_manager is not None}

    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List current collaborations tracked by the AgentManager (if any)."""
        if not self.new_agent_manager:
            return []
        try:
            active_collaborations = getattr(self.new_agent_manager, "active_collaborations", {})
            workflows = []
            for collab_id, collab in active_collaborations.items():
                workflows.append({
                    "workflow_id": collab_id,
                    "initiator": collab.initiator_id,
                    "agents": collab.target_agents,
                    "description": collab.task_description,
                    "mode": collab.mode.value,
                    "created_at": collab.created_at,
                })
            return workflows
        except Exception as e:
            logger.error(f"Failed to list active workflows: {e}")
            return []


# Global workflow bridge instance
workflow_bridge = None


def initialize_workflow_bridge(new_agent_manager=None, new_knowledge_graph=None):
    """Initialize and register a global WorkflowBridge instance."""
    global workflow_bridge
    workflow_bridge = WorkflowBridge(new_agent_manager, new_knowledge_graph)
    return workflow_bridge


def get_workflow_bridge() -> Optional[WorkflowBridge]:
    """Return the global WorkflowBridge instance if initialized."""
    return workflow_bridge
