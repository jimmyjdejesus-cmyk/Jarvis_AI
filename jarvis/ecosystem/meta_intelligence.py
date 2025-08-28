"""Lightweight meta‑intelligence layer.

The :class:`MetaAgent` acts as the entry point for missions. It can spawn
sub‑orchestrators for individual mission steps and also build arbitrary
execution graphs using the :class:`DynamicOrchestrator` template.

Only the minimal surface required by the tests is implemented – the agent can
plan directives, delegate mission steps and pursue curiosity driven tasks.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, Callable, Awaitable

from jarvis.agents.agent_resources import (
    AgentCapability,
    AgentMetrics,
    SystemEvolutionPlan,
    SystemHealth,
)
from jarvis.agents.base import AIAgent
from jarvis.agents.critics import (
    BlueTeamCritic,
    ConstitutionalCritic,
    CriticFeedback,
    CriticVerdict,
    RedTeamCritic,
    WhiteGate,
)
from jarvis.agents.curiosity_agent import CuriosityAgent
from jarvis.agents.curiosity_router import CuriosityRouter
from jarvis.agents.mission_planner import MissionPlanner
from jarvis.agents.specialist import SpecialistAgent
from jarvis.memory.project_memory import MemoryManager, ProjectMemory
from jarvis.monitoring.performance import CriticInsightMerger, PerformanceTracker
from jarvis.homeostasis import SystemMonitor
from jarvis.orchestration.orchestrator import (
    AgentSpec,
    DynamicOrchestrator,
    MultiAgentOrchestrator,
)
from jarvis.orchestration.sub_orchestrator import SubOrchestrator
from jarvis.persistence.session import SessionManager
from jarvis.world_model.knowledge_graph import KnowledgeGraph
from jarvis.world_model.hypergraph import HierarchicalHypergraph
from jarvis.workflows.engine import (
    WorkflowEngine,
    WorkflowStatus,
    add_custom_task,
    create_workflow,
)

logger = logging.getLogger(__name__)


class ExecutiveAgent(AIAgent):
    """Executive agent that manages other AI agents."""
def __init__(
        self,
        agent_id: str,
        mcp_client=None,
        orchestrator_cls: Type[MultiAgentOrchestrator] = SubOrchestrator,
        memory_manager: Optional[MemoryManager] = None,
        mission_planner: Optional['MissionPlanner'] = None,
        enable_red_team: bool | None = None,
        enable_blue_team: bool | None = None,
        blue_team_sensitivity: float = 0.5,
        enable_curiosity: bool | None = None,
        enable_curiosity_router: bool | None = None,
    ):
        super().__init__(agent_id, [
            AgentCapability.REASONING,
            AgentCapability.PLANNING,
            AgentCapability.MONITORING,
            AgentCapability.LEARNING,
        ])
        self.mcp_client = mcp_client
        self.orchestrator_cls = orchestrator_cls
        self.mission_planner = mission_planner or MissionPlanner()
        self.session_manager = SessionManager()
        self.constitutional_critic = ConstitutionalCritic(mcp_client=self.mcp_client)
        self.memory: MemoryManager = memory_manager or ProjectMemory()
        self.managed_agents: Dict[str, AIAgent] = {}
        self.evolution_plans: List[SystemEvolutionPlan] = []
        self.hypergraph = HierarchicalHypergraph()
        self.curiosity_agent = CuriosityAgent(self.hypergraph)
        self.curiosity_router: CuriosityRouter | None = None

        if (
            enable_red_team is None
            or enable_blue_team is None
            or enable_curiosity is None
            or enable_curiosity_router is None
        ):
            try:
                from config.config_loader import load_config
                cfg = load_config()
            except Exception:
                cfg = {}
            if enable_red_team is None:
                enable_red_team = cfg.get("ENABLE_RED_TEAM", False)
            if enable_blue_team is None:
                enable_blue_team = cfg.get("ENABLE_BLUE_TEAM", True)
            if enable_curiosity is None:
                enable_curiosity = cfg.get("ENABLE_CURIOSITY", True)
            if enable_curiosity_router is None:
                enable_curiosity_router = cfg.get("ENABLE_CURIOSITY_ROUTING", True)

        self.enable_curiosity = bool(enable_curiosity)
        self.enable_curiosity_router = bool(enable_curiosity_router)
        self.enable_red_team = bool(enable_red_team)
        self.red_team = RedTeamCritic(mcp_client) if self.enable_red_team else None
        self.enable_blue_team = bool(enable_blue_team)
        self.blue_team = (
            BlueTeamCritic(sensitivity=blue_team_sensitivity)
            if self.enable_blue_team
            else None
        )
        self.white_gate = WhiteGate()
        self.system_monitor = SystemMonitor()
        if self.mcp_client:
            self.mcp_client.monitor = self.system_monitor
        self._initialize_knowledge_graph()
        self.learning_history: List[Dict[str, Any]] = []
        self.sub_orchestrators: Dict[str, MultiAgentOrchestrator] = {}
        self.critic_merger = CriticInsightMerger()
        self.performance_tracker = PerformanceTracker()
        if self.enable_curiosity_router:
            self.curiosity_router = CuriosityRouter()
def log_event(self, event: str, payload: Any):
        """Log an event."""
        logger.info(f"Event '{event}': {payload}")

    def _initialize_knowledge_graph(self):
        """Connect to a persistent knowledge graph backend.

        Attempts to create a :class:`Neo4jGraph` using environment variables
        (``NEO4J_URI``, ``NEO4J_USER``, ``NEO4J_PASSWORD``). If the connection
        fails or the dependencies are unavailable, it falls back to the
        in-memory :class:`KnowledgeGraph` implementation.
        """

        try:
            from jarvis.world_model.neo4j_graph import Neo4jGraph

            if os.getenv("NEO4J_URI"):
                self.knowledge_graph = Neo4jGraph()
                return
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.warning("Neo4j backend unavailable: %s", exc)

        self.knowledge_graph = KnowledgeGraph()

    def manage_directive(self, directive_text: str, context: Dict[str, Any], session_id: str | None = None) -> Dict[str, Any]:
        """Break a directive into tasks and store the mission plan."""
        dag = self.mission_planner.plan(directive_text, context)
        tasks = dag.tasks
        graph = self.mission_planner.to_graph(tasks)
        critique = self.constitutional_critic.review({"tasks": tasks, "goal": directive_text})
        if critique.get("veto"):
            return {"success": False, "critique": critique}
        if session_id:
            plan = {"goal": directive_text, "tasks": tasks, "graph": graph}
            self.session_manager.save_mission_plan(session_id, plan)
        return {
            "success": True, "directive": directive_text, "tasks": tasks,
            "graph": graph, "critique": critique,
        }

    plan_mission = manage_directive

    async def execute_mission(self, directive: str, context: Dict[str, Any], session_id: str | None = None) -> Dict[str, Any]:
        """Plan and execute a mission using the workflow engine.

        The mission is first decomposed into a :class:`MissionDAG` by the
        :class:`MissionPlanner`. Each node in the DAG becomes a task in a
        :class:`WorkflowEngine` workflow, allowing branches without
        dependencies to run in parallel.

        Args:
            directive: High level mission objective.
            context: Additional mission context.
            session_id: Optional session identifier for persistence.

        Returns:
            Mission execution result dictionary.
        """
        # 1. Plan mission and build workflow
        dag = self.mission_planner.plan(directive, context)
        critique = await self.constitutional_critic.review(
            {"goal": directive, "nodes": list(dag.nodes.keys())}
        )
        if critique.get("veto"):
            return {"success": False, "critique": critique}

        workflow = create_workflow(name=directive)
        for node in dag.nodes.values():
            async def _task_fn(_ctx, mission_node=node):
                step = {
                    "step_id": mission_node.step_id,
                    "request": mission_node.capability,
                    "specialists": [],
                    "code": None,
                    "user_context": context.get("user_context"),
                }
                return await self._handle_mission_step(step)

            add_custom_task(
                workflow,
                task_id=node.step_id,
                name=node.capability,
                function=_task_fn,
                dependencies=node.deps,
            )

        # 2. Execute workflow via engine
        executed = await self.workflow_engine.execute_workflow(workflow)
        self._last_execution_workflow = executed

        mission_results = [
            executed.context.results[task_id].output
            for task_id in dag.nodes.keys()
            if task_id in executed.context.results
        ]

        if executed.status != WorkflowStatus.COMPLETED:
            logger.error("Mission '%s' failed.", directive)
            return {
                "success": False,
                "error": "Mission execution failed.",
                "results": mission_results,
            }

        logger.info("Mission '%s' completed successfully.", directive)

        if self.enable_curiosity:
            await self._consider_curiosity(mission_results)

        return {"success": True, "results": mission_results}

    def get_execution_graph(self) -> Dict[str, Any]:
        """Return graph of the last executed workflow."""
        if not self._last_execution_workflow:
            return {}

        workflow = self._last_execution_workflow
        nodes = {
            task.task_id: {
                "name": task.name,
                "status": task.status.value,
                "dependencies": task.dependencies,
            }
            for task in workflow.tasks
        }
        edges = [
            (dep, task.task_id)
            for task in workflow.tasks
            for dep in task.dependencies
        ]
        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value,
            "nodes": nodes,
            "edges": edges,
        }

    async def _consider_curiosity(self, mission_results: List[Dict[str, Any]]):
        """
        After a mission, check if there's an opportunity for curiosity-driven exploration.
        """
        if not self.enable_curiosity:
            logger.debug("Curiosity is disabled; skipping curiosity routing.")
            return

        if not (self.enable_curiosity_routing and self.curiosity_router):
            logger.debug("Curiosity routing disabled; no directive generated.")
            return

        question = self.curiosity_agent.generate_question()
if not question:
            logger.debug("Curiosity agent produced no question.")
            return

        directive = self.curiosity_router.route(question)
        logger.info("Curiosity agent generated directive: %s", directive)
        self.log_event("curiosity_triggered", {"question": question, "directive": directive})
        asyncio.create_task(self.execute_mission(directive, {}))

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute meta-level coordination tasks with optional risk critique."""
        task_type = task.get("type", "unknown")
        if task_type == "analyze_system":
            result = await self._analyze_system_performance()
        elif task_type == "optimize_agents":
            result = await self._optimize_agent_performance()
        elif task_type == "evolve_system":
            result = await self._evolve_system_capabilities()
        elif task_type == "create_agent":
            result = await self._create_new_agent(task)
        elif task_type == "mission_step":
            result = await self._handle_mission_step(task)
        elif task_type == "search_repository":
            query = task.get("query", "")
            k = task.get("k", 5)
            result = {"success": True, "results": self.search_repository(query, k)}
        elif task_type == "pursue_curiosity":
            question = self.curiosity_agent.generate_question()
            if question:
                result = self.manage_directive(question)
            else:
                result = {"success": False, "error": "No low-confidence items"}
        else:
            result = {"success": False, "error": f"Unknown meta-task: {task_type}"}

        critics: List[Dict[str, Any]] = []
        result["critic"] = {}
        red_verdict: CriticVerdict = CriticVerdict(True, [], 0.0, "")
        if self.red_team:
            try:
                red_verdict = await self.red_team.review(json.dumps(result), {})
            except Exception as exc:
                logger.error("Red team review failed: %s", exc)
                red_verdict = CriticVerdict(True, [], 0.0, "Critic error")
            result["critic"]["red"] = red_verdict.to_dict()
            if not red_verdict.approved:
                critics.append({
                    "critic_id": "red_team",
                    "message": "; ".join(red_verdict.fixes) or red_verdict.notes,
                    "severity": "high",
                })

        if critics:
            async def _retry() -> Dict[str, Any]:
                return await self.execute_task({**task, "_retry": True})

            synthesis = await self.integrate_critic_feedback(critics, retry_task=_retry)
            result["critic_synthesis"] = synthesis
            if "retry_result" in synthesis:
                return synthesis["retry_result"]

        blue_verdict: CriticVerdict
        if self.blue_team:
            blue_verdict = self.blue_team.review(result, {})
            result["critic"]["blue"] = blue_verdict.to_dict()
        else:
            blue_verdict = CriticVerdict(True, [], 0.0, "")

        result["critic"]["white"] = self.white_gate.merge(red_verdict, blue_verdict).to_dict()
        return result

    async def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from system-wide feedback"""
        # Meta-learning: analyze patterns across all agents
        for plan in self.evolution_plans:
            if plan.status == "executing":
                self._adjust_evolution_plan(plan, feedback)
        return True
    
    def _adjust_evolution_plan(self, plan: SystemEvolutionPlan, feedback: Dict[str, Any]):
        # Placeholder for adjusting evolution plan based on feedback
        pass

    async def _analyze_system_performance(self) -> Dict[str, Any]:
        """Analyze overall system performance"""
        analysis = {
            "total_agents": len(self.managed_agents),
            "active_agents": len([a for a in self.managed_agents.values() if a.is_active]),
            "average_performance": 0.0, "capability_coverage": {},
            "bottlenecks": [], "improvement_opportunities": []
        }
        if self.managed_agents:
            performances = [agent.metrics.overall_performance() for agent in self.managed_agents.values()]
            analysis["average_performance"] = sum(performances) / len(performances)
            for capability in AgentCapability:
                agents_with_capability = [
                    agent for agent in self.managed_agents.values()
                    if capability in agent.capabilities
                ]
                analysis["capability_coverage"][capability.value] = len(agents_with_capability)
            slow_agents = [
                agent for agent in self.managed_agents.values()
                if agent.metrics.average_response_time > 5.0
            ]
            analysis["bottlenecks"] = [agent.agent_id for agent in slow_agents]
            low_performing_agents = [
                agent for agent in self.managed_agents.values()
                if agent.metrics.overall_performance() < 0.7
            ]
            analysis["improvement_opportunities"] = [agent.agent_id for agent in low_performing_agents]
        return {"success": True, "analysis": analysis}

    async def _optimize_agent_performance(self) -> Dict[str, Any]:
        """Optimize individual agent performance"""
        optimizations = []
        for agent in self.managed_agents.values():
            if agent.metrics.overall_performance() < 0.8:
                optimization = {
                    "agent_id": agent.agent_id,
                    "current_performance": agent.metrics.overall_performance(),
                    "optimizations": []
                }
                if agent.metrics.success_rate < 0.9:
                    optimization["optimizations"].append("improve_accuracy")
                if agent.metrics.average_response_time > 3.0:
                    optimization["optimizations"].append("reduce_latency")
                if agent.metrics.resource_usage > 0.8:
                    optimization["optimizations"].append("optimize_resources")
                optimizations.append(optimization)
        return {"success": True, "optimizations": optimizations}

    async def _evolve_system_capabilities(self) -> Dict[str, Any]:
        """Plan and execute system evolution"""
        current_capabilities = set()
        for agent in self.managed_agents.values():
            current_capabilities.update(agent.capabilities)
        
        all_capabilities = set(AgentCapability)
        missing_capabilities = all_capabilities - current_capabilities
        
        if missing_capabilities:
            plan = SystemEvolutionPlan(
                plan_id=str(uuid.uuid4()),
                target_capabilities=list(missing_capabilities),
                required_agents=[f"agent_{cap.value}" for cap in missing_capabilities],
                optimization_targets={"performance": 0.9, "efficiency": 0.8},
                timeline=timedelta(hours=1)
            )
            self.evolution_plans.append(plan)
            return {
                "success": True,
                "evolution_plan": {
                    "plan_id": plan.plan_id,
                    "missing_capabilities": [cap.value for cap in missing_capabilities],
                    "timeline": str(plan.timeline)
                }
            }
        return {"success": True, "message": "System capabilities are complete"}

    async def _create_new_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent based on requirements"""
        required_capabilities = task.get("capabilities", [])
        agent_type = task.get("agent_type", "specialist")
        agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"

        if required_capabilities:
            capabilities = [
                AgentCapability(cap)
                for cap in required_capabilities
                if cap in [c.value for c in AgentCapability]
            ]
            specialization = required_capabilities[0] if required_capabilities else "general"
            new_agent = SpecialistAgent(
                agent_id=agent_id,
                specialization=specialization,
                capabilities=capabilities,
                knowledge_graph=self.knowledge_graph,
                mcp_client=self.mcp_client,
                preferred_models=[],  # Let's use default models for now
            )
            self.managed_agents[agent_id] = new_agent
            return {
                "success": True,
                "agent_id": agent_id,
                "capabilities": [cap.value for cap in capabilities],
            }
        return {"success": False, "error": "No valid capabilities specified"}

    def create_sub_orchestrator(self, name: str, spec: Dict[str, Any]) -> MultiAgentOrchestrator:
        orchestrator = self.orchestrator_cls(self.mcp_client, **spec)
        self.sub_orchestrators[name] = orchestrator
        return orchestrator

    async def _handle_mission_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single planned mission step.

        The step outcome is persisted to both the project memory and the
        knowledge graph for later retrieval.

        Args:
            step: Definition of the mission step including ``step_id`` and
                ``request``.

        Returns:
            A dictionary containing the step result and critique information.
        """
        step_id = step.get("step_id", uuid.uuid4().hex[:8])
        orchestrator = self.sub_orchestrators.get(step_id)
        if not orchestrator:
            spec = {
                "allowed_specialists": step.get("specialists"),
                "knowledge_graph": self.knowledge_graph,
                "memory": self.memory,
            }
            orchestrator = self.create_sub_orchestrator(step_id, spec)

        critique = self.constitutional_critic.review({"tasks": [step.get("request", "")]})
        if critique.get("veto"):
            return {"success": False, "critique": critique, "step_id": step_id}

        result = await orchestrator.coordinate_specialists(
            step.get("request", ""), step.get("code"), step.get("user_context"),
        )
        try:
            self.memory.add("mission", step_id, json.dumps(result))
        except Exception as exc:  # pragma: no cover - safety net
            logger.warning("Memory persistence failed for step %s: %s", step_id, exc)
        try:
            self.knowledge_graph.add_fact(step_id, "result", json.dumps(result))
        except Exception as exc:  # pragma: no cover - safety net
            logger.warning("KG persistence failed for step %s: %s", step_id, exc)

        return {"success": True, "result": result, "step_id": step_id, "critique": critique}

    def _record_strategy_from_trace(self, trace: List[str], confidence: float = 1.0) -> str:
        """Store a successful reasoning trace as a strategy node."""
        return self.hypergraph.add_strategy(trace, confidence)

    async def integrate_critic_feedback(
        self,
        feedback_items: List[Dict[str, Any]],
        retry_task: Optional[Callable[[], Awaitable[Any]]] = None,
    ) -> Dict[str, Any]:
        """Merge critic feedback and optionally retry a task."""
        feedback_objs = []
        for idx, item in enumerate(feedback_items):
            try:
                feedback_obj = CriticFeedback(**item)
                feedback_objs.append(feedback_obj)
            except TypeError as e:
                logger.error(
                    "Failed to construct CriticFeedback from feedback_items[%d]: %s. Item: %s",
                    idx,
                    e,
                    item,
                )
        if not feedback_objs:
            logger.warning(
                "No valid CriticFeedback objects could be constructed from feedback_items."
            )

        weighted = self.critic_merger.weight_feedback(feedback_objs)
        synthesis = self.critic_merger.synthesize_arguments(weighted)
        logger.info("Critic synthesis: %s", synthesis["combined_argument"])

        result: Dict[str, Any] = {"synthesis": synthesis}
        if retry_task and synthesis["max_severity"] in ("high", "critical"):
            try:
                retry_result = await self._adaptive_retry(
                    retry_task, synthesis["max_severity"]
                )
                result["retry_result"] = retry_result
            except Exception as e:
                result["retry_error"] = str(e)
        return result

    async def _adaptive_retry(
        self, task: Callable[[], Awaitable[Any]], severity: str, base_delay: float = 0.1
    ) -> Any:
        """Retry a task with backoff based on severity."""
        max_attempts = 3 if severity in ("high", "critical") else 1
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                result = await task()
                self.performance_tracker.record_event("retry", True, attempt)
                return result
            except Exception as e:
                self.performance_tracker.metrics["retry_attempts"] += 1
                logger.warning("Retry %s/%s failed: %s", attempt, max_attempts, e)
                if attempt >= max_attempts:
                    self.performance_tracker.record_event("retry", False, attempt)
                    raise


class MetaIntelligenceCore:
    """Core meta-intelligence system that manages the AI ecosystem"""
    def __init__(
        self, *, enable_red_team: bool = False, enable_blue_team: bool = True,
        blue_team_sensitivity: float = 0.5,
    ):
        self.meta_agent = ExecutiveAgent(
            "meta_core", enable_red_team=enable_red_team,
            enable_blue_team=enable_blue_team,
            blue_team_sensitivity=blue_team_sensitivity,
        )
        self.system_metrics: Dict[str, Any] = {}
        self.evolution_history: List[Dict[str, Any]] = []
        self.system_health = SystemHealth.OPTIMAL
        self.critic_merger = CriticInsightMerger()
        self.performance_tracker = PerformanceTracker()
        self._initialize_base_agents()

    def _initialize_base_agents(self):
        """Initialize the system with basic AI agents"""
        base_agents = [
            ("reasoning_agent", [AgentCapability.REASONING, AgentCapability.ANALYSIS]),
            ("creative_agent", [AgentCapability.CREATIVITY, AgentCapability.SYNTHESIS]),
            ("planning_agent", [AgentCapability.PLANNING, AgentCapability.EXECUTION]),
            ("learning_agent", [AgentCapability.LEARNING, AgentCapability.MONITORING])
        ]
        for agent_id, capabilities in base_agents:
            agent = SpecialistAgent(
                agent_id=agent_id,
                specialization=capabilities[0].value,
                capabilities=capabilities,
                knowledge_graph=self.meta_agent.knowledge_graph,
                mcp_client=self.meta_agent.mcp_client,
                preferred_models=[],
            )
            self.meta_agent.managed_agents[agent_id] = agent

    async def analyze_system_state(self) -> Dict[str, Any]:
        """Analyze the current state of the AI ecosystem"""
        analysis_task = {"type": "analyze_system"}
        analysis_result = await self.meta_agent.execute_task(analysis_task)
        self.performance_tracker.record_event(
            "analysis", success=analysis_result.get("success", False),
        )
        if analysis_result.get("success", False):
            avg_performance = analysis_result["analysis"]["average_performance"]
            if avg_performance > 0.9: self.system_health = SystemHealth.OPTIMAL
            elif avg_performance > 0.8: self.system_health = SystemHealth.GOOD
            elif avg_performance > 0.6: self.system_health = SystemHealth.DEGRADED
            else: self.system_health = SystemHealth.CRITICAL
        
        return {
            "system_health": self.system_health.value, "analysis": analysis_result,
            "total_agents": len(self.meta_agent.managed_agents),
            "active_agents": len([a for a in self.meta_agent.managed_agents.values() if a.is_active])
        }

    async def evolve_system(self) -> Dict[str, Any]:
        """Trigger system evolution and improvement"""
        evolution_task = {"type": "evolve_system"}
        evolution_result = await self.meta_agent.execute_task(evolution_task)
        self.performance_tracker.record_event(
            "evolution", success=evolution_result.get("success", False),
        )
        if evolution_result.get("success", False):
            self.evolution_history.append({
                "timestamp": datetime.now(), "evolution": evolution_result
            })
        return evolution_result

    async def create_specialized_agent(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new specialized agent based on requirements"""
        create_task = {
            "type": "create_agent", "capabilities": requirements.get("capabilities", []),
            "agent_type": requirements.get("type", "specialist")
        }
        return await self.meta_agent.execute_task(create_task)

    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize system-wide performance"""
        optimize_task = {"type": "optimize_agents"}
        return await self.meta_agent.execute_task(optimize_task)

    def record_successful_strategy(self, trace: List[str], confidence: float = 1.0) -> str:
        """Record a strategy node from a successful reasoning trace."""
        return self.meta_agent._record_strategy_from_trace(trace, confidence)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_statuses = {}
        for agent_id, agent in self.meta_agent.managed_agents.items():
            agent_statuses[agent_id] = {
                "performance": agent.metrics.overall_performance(),
                "success_rate": agent.metrics.success_rate,
                "response_time": agent.metrics.average_response_time,
                "capabilities": [cap.value for cap in agent.capabilities],
                "is_active": agent.is_active
            }
        return {
            "system_health": self.system_health.value,
            "meta_agent_performance": self.meta_agent.metrics.overall_performance(),
            "total_agents": len(self.meta_agent.managed_agents),
            "agents": agent_statuses,
            "evolution_plans": len(self.meta_agent.evolution_plans),
            "evolution_history": len(self.evolution_history),
            "performance_metrics": self.performance_tracker.metrics,
        }

    async def learn_from_ecosystem_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from ecosystem-wide feedback"""
        await self.meta_agent.learn_from_feedback(feedback)
        critics = feedback.get("critics")
        if critics:
            await self.integrate_critic_feedback(critics)
        for agent in self.meta_agent.managed_agents.values():
            await agent.learn_from_feedback(feedback)
        return True

    async def integrate_critic_feedback(
        self, feedback_items: List[Dict[str, Any]],
        retry_task: Optional[Callable[[], Awaitable[Any]]] = None,
    ) -> Dict[str, Any]:
        """Merge critic feedback and optionally retry a task."""
        feedback_objs = []
        for idx, item in enumerate(feedback_items):
            try:
                feedback_obj = CriticFeedback(**item)
                feedback_objs.append(feedback_obj)
            except TypeError as e:
                logger.error(
                    "Failed to construct CriticFeedback from feedback_items[%d]: %s. Item: %s",
                    idx, e, item
                )
        if not feedback_objs:
            logger.warning("No valid CriticFeedback objects could be constructed from feedback_items.")
        
        weighted = self.critic_merger.weight_feedback(feedback_objs)
        synthesis = self.critic_merger.synthesize_arguments(weighted)
        logger.info("Critic synthesis: %s", synthesis["combined_argument"])

        result: Dict[str, Any] = {"synthesis": synthesis}
        if retry_task and synthesis["max_severity"] in ("high", "critical"):
            try:
                retry_result = await self._adaptive_retry(retry_task, synthesis["max_severity"])
                result["retry_result"] = retry_result
            except Exception as e:
                result["retry_error"] = str(e)
        return result

    async def _adaptive_retry(
        self, task: Callable[[], Awaitable[Any]], severity: str, base_delay: float = 0.1
    ) -> Any:
        """Retry a task with backoff based on severity."""
        max_attempts = 3 if severity in ("high", "critical") else 1
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                result = await task()
                self.performance_tracker.record_event("retry", True, attempt)
                return result
            except Exception as e:
                self.performance_tracker.metrics["retry_attempts"] += 1
                logger.warning("Retry %s/%s failed: %s", attempt, max_attempts, e)
                if attempt >= max_attempts:
                    self.performance_tracker.record_event("retry", False, attempt)
                    raise
                await asyncio.sleep(base_delay * attempt)


# Global meta-intelligence instance
meta_intelligence = MetaIntelligenceCore()


# Convenience functions
async def analyze_ai_ecosystem() -> Dict[str, Any]:
    """Analyze the AI ecosystem state"""
    return await meta_intelligence.analyze_system_state()


async def evolve_ai_ecosystem() -> Dict[str, Any]:
    """Trigger AI ecosystem evolution"""
    return await meta_intelligence.evolve_system()