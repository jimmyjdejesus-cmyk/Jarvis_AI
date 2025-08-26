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
from jarvis.agents.critics import (
    BlueTeamCritic,
    ConstitutionalCritic,
    RedTeamCritic,
    CriticFeedback,
)
from jarvis.agents.curiosity_agent import CuriosityAgent
from jarvis.agents.mission_planner import MissionPlanner
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

logger = logging.getLogger(__name__)


class AIAgent:
    """Abstract base class for all AI agents."""

    def __init__(self, agent_id: str, capabilities: List[AgentCapability], knowledge_graph: Optional[KnowledgeGraph] = None):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.metrics = AgentMetrics(agent_id)
        self.created_at = datetime.now()
        self.is_active = True
        self.knowledge_graph = knowledge_graph

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results"""
        pass

    @abstractmethod
    async def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from feedback and adapt behavior"""
        pass

    def update_metrics(self, success: bool, response_time: float, resource_usage: float):
        """Update agent performance metrics"""
        alpha = 0.1
        if success:
            self.metrics.success_rate = (1 - alpha) * self.metrics.success_rate + alpha * 1.0
        else:
            self.metrics.success_rate = (1 - alpha) * self.metrics.success_rate + alpha * 0.0
        self.metrics.average_response_time = (
            (1 - alpha) * self.metrics.average_response_time + alpha * response_time
        )
        self.metrics.resource_usage = (
            (1 - alpha) * self.metrics.resource_usage + alpha * resource_usage
        )
        self.metrics.last_updated = datetime.now()

    def set_knowledge_graph(self, graph: KnowledgeGraph) -> None:
        """Attach a :class:`KnowledgeGraph` instance to this agent."""
        self.knowledge_graph = graph

    def query_knowledge_graph(self, query: str) -> Any:
        """Query the attached knowledge graph."""
        if not self.knowledge_graph:
            raise ValueError("KnowledgeGraph not available")
        return self.knowledge_graph.query(query)


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
        self.constitutional_critic = ConstitutionalCritic()
        self.memory: MemoryManager = memory_manager or ProjectMemory()
        self.managed_agents: Dict[str, AIAgent] = {}
        self.evolution_plans: List[SystemEvolutionPlan] = []
        self.hypergraph = HierarchicalHypergraph()
        self.curiosity_agent = CuriosityAgent(self.hypergraph)

        if enable_red_team is None or enable_blue_team is None:
            try:
                from config.config_loader import load_config
                cfg = load_config()
            except Exception:
                cfg = {}
            if enable_red_team is None:
                enable_red_team = cfg.get("ENABLE_RED_TEAM", False)
            if enable_blue_team is None:
                enable_blue_team = cfg.get("ENABLE_BLUE_TEAM", True)

        self.enable_red_team = bool(enable_red_team)
        self.red_team = RedTeamCritic(mcp_client) if self.enable_red_team else None
        self.enable_blue_team = bool(enable_blue_team)
        self.blue_team = (
            BlueTeamCritic(sensitivity=blue_team_sensitivity)
            if self.enable_blue_team
            else None
        )
        self.system_monitor = SystemMonitor()
        if self.mcp_client:
            self.mcp_client.monitor = self.system_monitor
        self._initialize_knowledge_graph()
        self.learning_history: List[Dict[str, Any]] = []
        self.sub_orchestrators: Dict[str, MultiAgentOrchestrator] = {}

    def _initialize_knowledge_graph(self):
        # Placeholder for KG initialization
        self.knowledge_graph = KnowledgeGraph()

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
            "success": True, "directive": directive_text, "tasks": tasks,
            "graph": graph, "critique": critique,
        }

    plan_mission = manage_directive

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
        if self.red_team:
            try:
                red_review = await self.red_team.review(self.agent_id, json.dumps(result))
            except Exception as exc:
                logger.error("Red team review failed: %s", exc)
                red_review = {"approved": True, "feedback": "Critic error"}
            result["red_team_review"] = red_review
            if not red_review.get("approved", True):
                critics.append({
                    "critic_id": "red_team", "message": red_review.get("feedback", ""),
                    "severity": "high",
                })

        if critics:
            result["critic_synthesis"] = await self.integrate_critic_feedback(critics)

        if self.blue_team:
            result["blue_team_evaluation"] = self.blue_team.evaluate(result)

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
            capabilities = [AgentCapability(cap) for cap in required_capabilities if cap in [c.value for c in AgentCapability]]
            new_agent = SpecialistAIAgent(agent_id, capabilities, self.knowledge_graph)
            self.managed_agents[agent_id] = new_agent
            return {
                "success": True, "agent_id": agent_id,
                "capabilities": [cap.value for cap in capabilities]
            }
        return {"success": False, "error": "No valid capabilities specified"}

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
            step.get("request", ""), step.get("code"), step.get("user_context"),
        )
        return {"success": True, "result": result, "step_id": step_id, "critique": critique}

    def _record_strategy_from_trace(self, trace: List[str], confidence: float = 1.0) -> str:
        """Store a successful reasoning trace as a strategy node."""
        return self.hypergraph.add_strategy(trace, confidence)


# This class seems to be a dependency for ExecutiveAgent, adding a placeholder
class SpecialistAIAgent(AIAgent):
    pass


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
            agent = SpecialistAIAgent(
                agent_id, capabilities, self.meta_agent.knowledge_graph
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