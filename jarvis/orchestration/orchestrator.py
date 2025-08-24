"""Reusable orchestration templates.

This module provides two lightweight orchestration helpers used throughout the
test-suite:

``MultiAgentOrchestrator``
    Coordinates a dictionary of specialist agents and records the reasoning
    path of each run.  It exposes a small API focused on the needs of the unit
    tests – coordinating specialists, tracking path memory and managing child
    orchestrators.

``DynamicOrchestrator``
    Builds LangGraph workflows from simple ``AgentSpec`` definitions.  It is a
    minimal wrapper that compiles an execution graph at runtime allowing tests
    to define arbitrary workflows.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional

# Orchestration Package
"""
Multi-agent orchestration system for coordinating specialist AI agents

This package provides:
- MultiAgentOrchestrator: Coordinates multiple specialists for complex tasks
- SubOrchestrator: Scoped orchestrator used for nested missions
- Workflow management and task delegation
- Result synthesis and conflict resolution
This package provides building blocks for creating LangGraph based
orchestration workflows.  The previous specialised orchestrator has been
replaced by a small, generic template which can dynamically assemble graphs
from ``AgentSpec`` definitions.
"""

from importlib import import_module
from types import ModuleType
from typing import Any

__all__ = [
    "AgentSpec",
    "DynamicOrchestrator",
    "MultiAgentOrchestrator",
    "SubOrchestrator",
    "PathMemory",
    "MessageBus",
    "HierarchicalMessageBus",
    "Event",
    "BandwidthLimitedChannel",
    "MissionPlanner",
    "RedisTaskQueue",
    "END",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin wrapper
    mapping = {
        "AgentSpec": (".orchestrator", "AgentSpec"),
        "DynamicOrchestrator": (".orchestrator", "DynamicOrchestrator"),
        "MultiAgentOrchestrator": (".orchestrator", "MultiAgentOrchestrator"),
        "END": (".orchestrator", "END"),
        "SubOrchestrator": (".sub_orchestrator", "SubOrchestrator"),
        "PruningManager": (".pruning", "PruningManager"),
        "PathMemory": (".path_memory", "PathMemory"),
        "MessageBus": (".message_bus", "MessageBus"),
        "HierarchicalMessageBus": (".message_bus", "HierarchicalMessageBus"),
        "Event": (".message_bus", "Event"),
        "BandwidthLimitedChannel": (".bandwidth_channel", "BandwidthLimitedChannel"),
        "MissionPlanner": (".mission_planner", "MissionPlanner"),
        "RedisTaskQueue": (".task_queue", "RedisTaskQueue"),
    }
    if name not in mapping:
        raise AttributeError(f"module 'jarvis.orchestration' has no attribute {name}")
    module_name, attr = mapping[name]
    module: ModuleType = import_module(module_name, __name__)
    value = getattr(module, attr)
    globals()[name] = value
    return value
from langgraph.graph import END, StateGraph

from .path_memory import PathMemory

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Multi agent orchestration
# ---------------------------------------------------------------------------


class MultiAgentOrchestrator:
    """Coordinate a collection of specialist agents.

    Parameters
    ----------
    mcp_client:
        Client used by specialists.
    specialists:
        Optional mapping of specialist name to the object implementing
        ``process_task``.
    """

    def __init__(
        self,
        mcp_client: Any,
        monitor: Any | None = None,
        knowledge_graph: Any | None = None,
        specialists: Optional[Dict[str, Any]] = None,
    ) -> None:
        from jarvis.agents.request_classifier import RequestClassifier  # Local import

        self.mcp_client = mcp_client
        self.monitor = monitor
        self.knowledge_graph = knowledge_graph
        self.specialists: Dict[str, Any] = specialists or {}
        self.child_orchestrators: Dict[str, "SubOrchestrator"] = {}
        self.request_classifier = RequestClassifier(list(self.specialists.keys()))
        self.collaboration_patterns = defaultdict(int)

    def list_child_orchestrators(self) -> List[str]:
        """List identifiers of active child orchestrators."""
        return list(self.child_orchestrators.keys())

    async def run_child_orchestrator(
        self,
        name: str,
        request: str,
        *,
        context: Any | None = None,
        user_context: str | None = None,
    ) -> Dict[str, Any]:
        """Execute a task using a registered child orchestrator."""
        orchestrator = self.child_orchestrators.get(name)
        if orchestrator is None:
            raise ValueError(f"Unknown child orchestrator: {name}")

        return await orchestrator.coordinate_specialists(
            request,
            context=context,
            user_context=user_context,
        )

self.task_history = []
        self.active_collaborations = {}
        self.exploration_stats: List[Dict[str, float]] = []

    async def analyze_request_complexity(self, request: str, code: str = None) -> Dict[str, Any]:
        """Analyze a request using the :class:`RequestClassifier`."""
        return self.request_classifier.classify(request, code)

    async def coordinate_specialists(
        self,
        request: str,
        code: str | None = None,
        user_context: str | None = None,
        context: Any | None = None,
        novelty_boost: float = 0.0,
    ) -> Dict[str, Any]:
        """Coordinate multiple specialists to handle complex request."""
        analysis = await self.analyze_request_complexity(request, code)
        analysis["coordination_type"] = self._determine_coordination_type(
            analysis["specialists_needed"], analysis["complexity"]
        )
        analysis["collaboration_depth"] = self._determine_collaboration_depth(
            analysis["specialists_needed"]
        )

        path_memory = PathMemory()
        for spec in analysis["specialists_needed"]:
            path_memory.add_step(spec)

        avoid, similarity = (False, 0.0)
        if analysis["specialists_needed"]:
            avoid, similarity = path_memory.should_avoid()
            if avoid and novelty_boost <= 0.0:
                return self._create_error_response(
                    f"Previously failed path detected (similarity: {similarity:.2f}) - novelty boost required",
                    request,
                )

        if not analysis["specialists_needed"]:
            return self._create_simple_response(request)

        logger.info(
            f"Coordinating {len(analysis['specialists_needed'])} specialists for {analysis['complexity']} complexity task"
        )

        if analysis["coordination_type"] == "single":
            result = await self._single_specialist_analysis(
                request, analysis, path_memory, code, user_context, context
            )
        elif analysis["coordination_type"] == "parallel":
            result = await self._parallel_specialist_analysis(
                request, analysis, path_memory, code, user_context, context
            )
        else:  # sequential
            result = await self._sequential_specialist_analysis(
                request, analysis, path_memory, code, user_context, context
            )

        score = result.get("oracle_score", 1.0 if result.get("type") != "error" else 0.0)
        path_memory.record(score)
        return result

    async def dispatch_specialist(
        self,
        specialist_type: str,
        task: str,
        *,
        context: Any | None = None,
        user_context: str | None = None,
        models: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Execute a task with the requested specialist."""
        if specialist_type in self.specialists:
            specialist = self.specialists[specialist_type]
            kwargs = {"context": context, "user_context": user_context}
            if models is not None:
                kwargs["models"] = models
            return await specialist.process_task(task, **kwargs)
        if specialist_type in self.child_orchestrators:
            return await self.run_child_orchestrator(
                specialist_type, task, context=context, user_context=user_context
            )
        raise ValueError(f"Unknown specialist or orchestrator: {specialist_type}")

    def create_child_orchestrator(self, name: str, spec: Dict[str, Any]):
        """Create and register a child :class:`SubOrchestrator`."""
        from .sub_orchestrator import SubOrchestrator  # Local import to avoid cycle

        child = SubOrchestrator(self.mcp_client, **spec)
        self.child_orchestrators[name] = child
        return child

    def remove_child_orchestrator(self, name: str) -> bool:
        """Remove a child orchestrator by name."""
        return self.child_orchestrators.pop(name, None) is not None

    def _determine_coordination_type(self, specialists: List[str], complexity: str) -> str:
        """Determine how specialists should be coordinated"""
        if len(specialists) <= 1:
            return "single"
        elif len(specialists) == 2 and complexity in ["low", "medium"]:
            return "parallel"
        elif complexity == "high" or len(specialists) > 3:
            return "sequential"
        else:
            return "parallel"

    def _determine_collaboration_depth(self, specialists: List[str]) -> str:
        """Determine depth of collaboration between specialists"""
        if len(specialists) <= 1:
            return "none"
        elif len(specialists) == 2:
            return "basic"
        elif len(specialists) <= 3:
            return "moderate"
        else:
            return "deep"

    def _route_model_preferences(self, specialist, complexity: str) -> List[str]:
        """Determine model order based on system resources and task complexity."""
        models = list(specialist.preferred_models)
        local = [m for m in models if specialist._get_server_for_model(m) == "ollama"]
        cloud = [m for m in models if specialist._get_server_for_model(m) != "ollama"]

        snapshot = self.monitor.snapshot() if self.monitor else None
        if snapshot and snapshot.cpu > 80 and complexity != "high":
            return local + cloud
        if complexity == "high":
            return cloud + local
        return local + cloud

    async def _single_specialist_analysis(
        self, request: str, analysis: Dict, path_memory: PathMemory, code: str | None,
        user_context: str | None, context: Any | None
    ) -> Dict[str, Any]:
        specialist_type = analysis["specialists_needed"][0]
        task = self._create_specialist_task(request, code, user_context)
        try:
            result = await self.dispatch_specialist(
                specialist_type, task, context=context, user_context=user_context
            )
            path_memory.add_decisions(result.get("suggestions", [])[:3])

            candidate = Candidate(
                agent=specialist_type,
                bid=float(result.get("confidence", 0.0)),
                content=result.get("response", ""),
            )
            auction = run_vickrey_auction([candidate])
            self.exploration_stats.append(auction.metrics)

           return {
                "type": "parallel_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": merged,
                "confidence": auction.winner.bid,
                "coordination_summary": f"Auction won by {auction.winner.agent}",
                "auction": {"winner": auction.winner.agent, "price": auction.price},
                "exploration_metrics": auction.metrics,
            }
        except Exception as e:
            logger.error(f"Single specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)

    async def _parallel_specialist_analysis(
        self, request: str, analysis: Dict, path_memory: PathMemory, code: str | None,
        user_context: str | None, context: Any | None
    ) -> Dict[str, Any]:
        specialists_needed = analysis["specialists_needed"]
        task = self._create_specialist_task(request, code, user_context)

        grouped: Dict[tuple, List[tuple]] = defaultdict(list)
        for specialist_type in specialists_needed:
            specialist = self.specialists[specialist_type]
            models = self._route_model_preferences(specialist, analysis["complexity"])
            prompt = specialist.build_prompt(task, context, user_context)
            primary_model = models[0]
            server = specialist._get_server_for_model(primary_model)
            grouped[(server, primary_model)].append((specialist_type, specialist, prompt, models))

        try:
            batch_tasks, group_info = [], []
            for (server, model), items in grouped.items():
                prompts = [it[2] for it in items]
                batch_tasks.append(self.mcp_client.generate_response_batch(server, model, prompts))
                group_info.append((server, model, items))

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            specialist_results, successful_results = {}, []
            for (server, model, items), responses in zip(group_info, batch_results):
                if isinstance(responses, Exception):
                    logger.error(f"Batch {server}/{model} failed: {responses}")
                    for stype, spec, _, mods in items:
                        try:
                            res = await spec.process_task(task, context=context, user_context=user_context, models=mods)
                        except Exception as e:
                            res = self._create_specialist_error(stype, str(e))
                        specialist_results[stype] = res
                        if res.get("type") != "error":
                            successful_results.append(res)
                            path_memory.add_decisions(res.get("suggestions", [])[:3])
                    continue

for (specialist_type, specialist, _, _), response in zip(
                    items, responses
                ):
                    result = specialist.process_model_response(
                        response, model, task
                    )
                    specialist_results[specialist_type] = result
                    successful_results.append(result)
                    path_memory.add_decisions(
                        result.get("suggestions", [])[:3]
                    )

            candidates = [
                Candidate(
                    agent=res.get("specialist", "unknown"),
                    bid=float(res.get("confidence", 0.0)),
                    content=res.get("response", ""),
                )
                for res in successful_results
            ]
            auction = run_vickrey_auction(candidates)
            self.exploration_stats.append(auction.metrics)
            merged = "\n\n".join(
                f"{c.agent}: {c.content}" for c in auction.rankings
            )

            synthesized_response = await self._synthesize_parallel_results(request, successful_results)
            overall_confidence = self._calculate_overall_confidence(successful_results)
            return {
return {
                "type": "parallel_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": merged,
                "confidence": auction.winner.bid,
                "coordination_summary": f"Auction won by {auction.winner.agent}",
                "auction": {"winner": auction.winner.agent, "price": auction.price},
                "exploration_metrics": auction.metrics,
            }
        except Exception as e:
            logger.error(f"Parallel specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)

    async def _sequential_specialist_analysis(
        self, request: str, analysis: Dict, path_memory: PathMemory, code: str | None,
        user_context: str | None, context: Any | None
    ) -> Dict[str, Any]:
        specialists_needed = analysis["specialists_needed"]
        shared_context = [] if context is None else [context]
        specialist_results = {}
        task = self._create_specialist_task(request, code, user_context)

        try:
            for specialist_type in specialists_needed:
                specialist = self.specialists.get(specialist_type)
                models = self._route_model_preferences(specialist, analysis["complexity"]) if specialist else None

                result = await self.dispatch_specialist(
                    specialist_type, task, context=shared_context, user_context=user_context, models=models
                )
                specialist_results[specialist_type] = result

                decisions = result.get("suggestions", [])[:3]
                shared_context.append({
                    "specialist": specialist_type, "key_points": decisions,
                    "confidence": result.get("confidence", 0.7),
                    "priority_issues": result.get("priority_issues", [])[:2],
                })
                path_memory.add_decisions(decisions)
                logger.info(f"Completed {specialist_type} analysis, passing context to next specialist")

            synthesized_response = await self._synthesize_sequential_results(request, specialist_results)
return {
                "type": "sequential_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": synthesized_response,
                "confidence": auction.winner.bid,
                "coordination_summary": f"Auction won by {auction.winner.agent} after sequential analysis",
                "auction": {"winner": auction.winner.agent, "price": auction.price},
                "exploration_metrics": auction.metrics,
            }
            }
        except Exception as e:
            logger.error(f"Sequential specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)

    def _create_specialist_task(self, request: str, code: str = None, user_context: str = None) -> str:
        task_parts = [request]
        if code:
            task_parts.append(f"\n**Code to Analyze:**\n```\n{code}\n```")
        if user_context:
            task_parts.append(f"\n**Additional Context:**\n{user_context}")
        return "\n".join(task_parts)

    async def _synthesize_parallel_results(self, original_request: str, results: List[Dict]) -> str:
        if not results:
            return "No successful analysis results to synthesize."
        
        prompt = f"**MULTI-SPECIALIST ANALYSIS SYNTHESIS**\n\nOriginal Request: {original_request}\n\n**Specialist Insights:**\n"
        for res in results:
            specialist = res.get("specialist", "unknown")
            confidence = res.get("confidence", 0.0)
            response = res.get("response", "No response")[:300]
            prompt += f"\n**{specialist.title()} Expert** (confidence: {confidence:.2f}):\n{response}...\n"
        
        prompt += "\n\n**Your Task:** Synthesize these expert opinions into a comprehensive, actionable response..."
        try:
            return await self.mcp_client.generate_response("ollama", "llama3.2", prompt)
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return self._create_fallback_synthesis(results)

    async def _synthesize_sequential_results(self, original_request: str, results: Dict[str, Dict]) -> str:
        prompt = f"**SEQUENTIAL MULTI-SPECIALIST ANALYSIS SYNTHESIS**\n\nOriginal Request: {original_request}\n\n**Sequential Expert Analysis:**\n"
        for stype, res in results.items():
            confidence = res.get("confidence", 0.0)
            response = res.get("response", "No response")[:300]
            prompt += f"\n**{stype.title()} Expert** (confidence: {confidence:.2f}):\n{response}...\n"
        
        prompt += "\n\n**Your Task:** Synthesize this sequential analysis into a comprehensive response..."
        try:
            return await self.mcp_client.generate_response("ollama", "llama3.2", prompt)
        except Exception as e:
            logger.error(f"Sequential synthesis failed: {e}")
            return self._create_fallback_synthesis(list(results.values()))

    def _create_fallback_synthesis(self, results: List[Dict]) -> str:
        synthesis = "## Multi-Specialist Analysis Summary\n\n"
        for res in results:
            specialist = res.get("specialist", "unknown")
            suggestions = res.get("suggestions", [])
            issues = res.get("priority_issues", [])
            synthesis += f"### {specialist.title()} Expert Insights:\n"
            if suggestions:
                synthesis += "**Key Recommendations:**\n" + "".join(f"- {s}\n" for s in suggestions[:3])
            if issues:
                synthesis += "**Priority Issues:**\n" + "".join(f"- {i.get('description', 'Unknown')}\n" for i in issues[:2])
            synthesis += "\n"
        synthesis += "**Next Steps:** Review each specialist's recommendations..."
        return synthesis

    def _calculate_overall_confidence(self, results: List[Dict]) -> float:
        if not results: return 0.0
        confidences = [r.get("confidence", 0.5) for r in results]
        base_confidence = sum(confidences) / len(confidences)
        if len(results) > 1:
            base_confidence += min(0.1 * (len(results) - 1), 0.3)
        return min(base_confidence, 1.0)

    def _create_simple_response(self, request: str) -> Dict[str, Any]:
        return {
            "type": "simple", "complexity": "low", "specialists_used": [], "results": {},
            "synthesized_response": f"This appears to be a simple request: {request}",
            "confidence": 0.6, "coordination_summary": "No specialist coordination needed"
        }

    def _create_error_response(self, error_msg: str, request: str) -> Dict[str, Any]:
        return {
            "type": "error", "complexity": "unknown", "specialists_used": [], "results": {},
            "synthesized_response": f"I apologize, but I encountered an error: {error_msg}",
            "confidence": 0.0, "error": True, "coordination_summary": f"Coordination failed: {error_msg}"
        }

    def _create_specialist_error(self, specialist_type: str, error_msg: str) -> Dict[str, Any]:
        return {
            "specialist": specialist_type, "response": f"Analysis failed: {error_msg}",
            "confidence": 0.0, "suggestions": [], "priority_issues": [], "error": True
        }

    def get_specialist_status(self) -> Dict[str, Any]:
        status = {name: spec.get_specialization_info() for name, spec in self.specialists.items()}
        return {
            "available_specialists": list(self.specialists.keys()), "specialist_details": status,
            "total_tasks_completed": sum(len(s.task_history) for s in self.specialists.values()),
            "collaboration_patterns": self.collaboration_patterns
        }

    async def health_check_specialists(self) -> Dict[str, Any]:
        health_results = {}
        for name, specialist in self.specialists.items():
            try:
                result = await specialist.process_task("Health check test")
                health_results[name] = {"status": "healthy", "confidence": result.get("confidence", 0.0)}
            except Exception as e:
                health_results[name] = {"status": "error", "error": str(e)}
        
        overall_health = "healthy" if all(h["status"] == "healthy" for h in health_results.values()) else "degraded"
        return {"overall_status": overall_health, "specialists": health_results, "timestamp": datetime.now().isoformat()}

# ---------------------------------------------------------------------------
# Dynamic execution graphs
# ---------------------------------------------------------------------------

AgentCallable = Callable[[Dict[str, Any]], Dict[str, Any] | Awaitable[Dict[str, Any]]]

@dataclass
class AgentSpec:
    """Specification for a single node in the workflow."""
    name: str
    fn: AgentCallable
    next: Optional[str] = None
    condition: Optional[Callable[[Dict[str, Any]], str]] = None
    branches: Optional[Dict[str, Any]] = None
    entry: bool = False

class DynamicOrchestrator:
    """Compile and run LangGraph workflows from ``AgentSpec`` objects."""
    def __init__(self, agent_specs: List[AgentSpec]):
        self.agent_specs = agent_specs
        graph = StateGraph(dict)
        for spec in agent_specs:
            graph.add_node(spec.name, spec.fn)

        entry = next((s.name for s in agent_specs if s.entry), agent_specs[0].name)
        graph.set_entry_point(entry)

        for spec in agent_specs:
            if spec.next:
                graph.add_edge(spec.name, spec.next)
            if spec.condition and spec.branches:
                graph.add_conditional_edges(spec.name, spec.condition, spec.branches)

        self.workflow = graph.compile()

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the compiled workflow and return the final state."""
        logger.debug("Starting workflow with state: %s", state)
        result = await self.workflow.ainvoke(state)
        logger.debug("Workflow completed with state: %s", result)
        return result

__all__ = ["AgentSpec", "DynamicOrchestrator", "MultiAgentOrchestrator", "END"]
