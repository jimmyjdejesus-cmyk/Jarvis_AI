"""Lightweight meta‑intelligence layer.

The :class:`MetaAgent` acts as the entry point for missions.  It can spawn
sub‑orchestrators for individual mission steps and also build arbitrary
execution graphs using the :class:`DynamicOrchestrator` template.

Only the minimal surface required by the tests is implemented – the agent can
plan directives, delegate mission steps and pursue curiosity driven tasks.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jarvis.agents.curiosity_agent import CuriosityAgent
from jarvis.agents.critics import ConstitutionalCritic
from jarvis.agents.mission_planner import MissionPlanner
from jarvis.persistence.session import SessionManager
from jarvis.world_model.hypergraph import HierarchicalHypergraph

from jarvis.orchestration.orchestrator import (
    AgentSpec,
    DynamicOrchestrator,
    MultiAgentOrchestrator,
)
from jarvis.orchestration.sub_orchestrator import SubOrchestrator


class MetaAgent:
    """Coordinator capable of spawning orchestrators and executing graphs."""

    def __init__(
        self,
        agent_id: str,
        mcp_client: Any | None = None,
        orchestrator_cls: type[MultiAgentOrchestrator] = SubOrchestrator,
        mission_planner: MissionPlanner | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.mcp_client = mcp_client
        self.orchestrator_cls = orchestrator_cls
        self.mission_planner = mission_planner or MissionPlanner()
        self.session_manager = SessionManager()
        self.constitutional_critic = ConstitutionalCritic()

        self.sub_orchestrators: Dict[str, MultiAgentOrchestrator] = {}
        self.execution_graphs: Dict[str, DynamicOrchestrator] = {}

        self.hypergraph = HierarchicalHypergraph()
        self.curiosity_agent = CuriosityAgent(self.hypergraph)

    # ------------------------------------------------------------------
    def manage_directive(self, directive_text: str, session_id: str | None = None) -> Dict[str, Any]:
        """Break a directive into tasks and store the mission plan."""

        tasks = self.mission_planner.plan(directive_text)
        graph = self.mission_planner.to_graph(tasks)
        critique = self.constitutional_critic.review({"tasks": tasks, "goal": directive_text})
        if critique.get("veto"):
            return {"success": False, "critique": critique}
        if session_id:
            plan = {"goal": directive_text, "tasks": tasks, "graph": graph}
            self.session_manager.save_mission_plan(session_id, plan)
        return {
            "success": True,
            "directive": directive_text,
            "tasks": tasks,
            "graph": graph,
            "critique": critique,
        }

    # Backwards compatibility name used in some tests
    plan_mission = manage_directive

    # ------------------------------------------------------------------
    def create_sub_orchestrator(self, name: str, spec: Dict[str, Any]) -> MultiAgentOrchestrator:
        orchestrator = self.orchestrator_cls(self.mcp_client, **spec)
        self.sub_orchestrators[name] = orchestrator
        return orchestrator

    async def _handle_mission_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        step_id = step.get("step_id", uuid.uuid4().hex[:8])
        orchestrator = self.sub_orchestrators.get(step_id)
        if not orchestrator:
            spec = {"allowed_specialists": step.get("specialists")}
            orchestrator = self.create_sub_orchestrator(step_id, spec)

        critique = self.constitutional_critic.review({"tasks": [step.get("request", "")]})
        if critique.get("veto"):
            return {"success": False, "critique": critique, "step_id": step_id}

        result = await orchestrator.coordinate_specialists(
            step.get("request", ""),
            step.get("code"),
            step.get("user_context"),
        )
        return {"success": True, "result": result, "step_id": step_id, "critique": critique}

    # ------------------------------------------------------------------
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute meta-level coordination tasks."""

        task_type = task.get("type")
        if task_type == "mission_step":
            return await self._handle_mission_step(task)
        if task_type == "pursue_curiosity":
            question = self.curiosity_agent.generate_question()
            if question:
                return self.manage_directive(question)
            return {"success": False, "error": "No low-confidence items"}
        return {"success": False, "error": f"Unknown meta-task: {task_type}"}

    # ------------------------------------------------------------------
    def create_execution_graph(self, name: str, specs: List[Dict[str, Any]]) -> None:
        """Compile an execution graph from ``AgentSpec`` definitions."""

        agent_specs = [AgentSpec(**spec) for spec in specs]
        self.execution_graphs[name] = DynamicOrchestrator(agent_specs)

    async def delegate(self, name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run a previously compiled execution graph."""

        orchestrator = self.execution_graphs[name]
        return await orchestrator.run(state)


# Backwards compatibility
ExecutiveAgent = MetaAgent

