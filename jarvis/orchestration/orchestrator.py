# flake8: noqa

"""
This module provides two lightweight orchestration helpers:

- ``MultiAgentOrchestrator``: Coordinates a dictionary of specialist agents,
  records the reasoning path, and manages specialist coordination.
- ``DynamicOrchestrator``: Builds and runs LangGraph workflows from simple
  ``AgentSpec`` definitions, primarily for testing arbitrary workflows.
"""

# flake8: noqa: E501

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import json
from collections import defaultdict
from dataclasses import dataclass

from langgraph.graph import END  # noqa: F401
from jarvis.scoring.vickrey_auction import Candidate, run_vickrey_auction
from .path_memory import PathMemory
from .semantic_cache import SemanticCache
from .message_bus import HierarchicalMessageBus
from jarvis.memory.project_memory import ProjectMemory
from jarvis.agents.specialist_registry import (
    get_specialist_registry,
    create_specialist,
)
from jarvis.monitoring.performance import PerformanceTracker
from jarvis.agents.critics.constitutional_critic import ConstitutionalCritic

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub optional dependencies
sys.modules.setdefault("neo4j", MagicMock())
keyring_errors = types.ModuleType("keyring.errors")

class DynamicOrchestrator:
    """Placeholder dynamic orchestrator for tests."""

    pass


if TYPE_CHECKING:  # pragma: no cover - used only for type hints
    from .sub_orchestrator import SubOrchestrator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Orchestrator template
# ---------------------------------------------------------------------------


@dataclass
class StepContext:
    """Execution context for a single DAG step."""

    request: str
    allowed_specialists: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    budgets: Optional[Dict[str, Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None
    prune_policy: Optional[Dict[str, Any]] = None
    auction_policy: Optional[Dict[str, Any]] = None
    recursion_depth: int = 0
    user_context: Optional[str] = None
    context: Any | None = None
    timeout: Optional[float] = None


@dataclass
class StepResult:
    """Result of executing a step."""

    data: Dict[str, Any]
    run_id: str
    depth: int


class OrchestratorTemplate:
    """Base interface for orchestrators used in DAG execution."""

    async def run_step(self, step_ctx: StepContext) -> StepResult:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Multi agent orchestration
# ---------------------------------------------------------------------------


class MultiAgentOrchestrator(OrchestratorTemplate):
    """Coordinate a collection of specialist agents."""

    def __init__(
        self,
        mcp_client: Any,
        monitor: Any | None = None,
        knowledge_graph: Any | None = None,
        specialists: Optional[Dict[str, Any]] = None,
        *,
        message_bus: HierarchicalMessageBus | None = None,
        budgets: Optional[Dict[str, Any]] = None,
        memory: Optional[ProjectMemory] = None,
        performance_tracker: PerformanceTracker | None = None,
    ) -> None:
        self.mcp_client = mcp_client
        self.monitor = monitor
        self.knowledge_graph = knowledge_graph
        self.memory = memory
        if specialists is None:
            self.specialists = {
                name: create_specialist(
                    name, mcp_client, knowledge_graph=knowledge_graph
                )
                for name in get_specialist_registry()
            }
        else:
            self.specialists = specialists
        self.semantic_cache = SemanticCache()
        self.child_orchestrators: Dict[str, "SubOrchestrator"] = {}
        self.collaboration_patterns = defaultdict(int)
        self.task_history = []
        self.active_collaborations = {}
        self.exploration_stats: List[Dict[str, float]] = []
        self.message_bus = message_bus or HierarchicalMessageBus()
        self.budgets = budgets or {}
        self.performance_tracker = performance_tracker or PerformanceTracker()
        self.critic = ConstitutionalCritic(mcp_client=self.mcp_client)

    async def log_event(
        self,
        event: str,
        payload: Any,
        *,
        run_id: Optional[str] = None,
        step_id: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> None:
        """Publish an event to the hierarchical message bus."""
        await self.message_bus.publish(
            event,
            payload,
            run_id=run_id,
            step_id=step_id,
            parent_id=parent_id,
        )

    async def run_step(self, step_ctx: StepContext) -> StepResult:
        """Execute a single orchestration step with retry and timeout control."""
        run_id = step_ctx.budgets.get("run_id") if step_ctx.budgets else None
        allowed = step_ctx.allowed_specialists
        original_specialists = self.specialists
        if allowed is not None:
            self.specialists = {
                name: agent
                for name, agent in original_specialists.items()
                if name in set(allowed)
            }

        retry_policy = step_ctx.retry_policy or {}
        retries = retry_policy.get("retries", 0)
        backoff_base = retry_policy.get("backoff_base", 1)
        timeout = step_ctx.timeout or retry_policy.get("timeout")

        attempt = 0
        try:
            while True:
                attempt += 1
                try:
                    coro = self.coordinate_specialists(
                        step_ctx.request,
                        context=step_ctx.context,
                        user_context=step_ctx.user_context,
                    )
                    if timeout is not None:
                        data = await asyncio.wait_for(coro, timeout)
                    else:
                        data = await coro
                    self.performance_tracker.record_event(
                        "step", True, attempt)
                    break
                except Exception as e:
                    if isinstance(e, asyncio.CancelledError):
                        raise
                    self.performance_tracker.record_event(
                        "step", False, attempt)
                    if attempt > retries:
                        raise
                    delay = backoff_base * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)
        finally:
            self.specialists = original_specialists

        await self.log_event(
            "orchestrator.step.completed",
            {"specialists_used": data.get("specialists_used", [])},
            run_id=run_id,
        )
        return StepResult(
            data=data,
            run_id=run_id or "",
            depth=step_ctx.recursion_depth)

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

    def spawn_child_orchestrator(
            self, parent_run_id: str, spec: Dict[str, Any]):
        """Spawn a child orchestrator inheriting this orchestrator's context."""
        child = self.create_child_orchestrator(parent_run_id, spec)

        async def forward(
                event: str,
                payload: Any,
                *,
                run_id: Optional[str] = None,
                step_id: Optional[str] = None):
            await self.log_event(
                f"child.{parent_run_id}.{event}",
                payload,
                run_id=run_id,
                step_id=step_id,
                parent_id=parent_run_id,
            )

        child.log_event = forward  # type: ignore[attr-defined]
        child.message_bus = self.message_bus
        child.budgets = {**self.budgets, **spec.get("budgets", {})}
        return child

    async def _analyze_request_complexity(
            self, request: str, code: str = None) -> Dict[str, Any]:
        """Analyze a request to determine complexity and specialists needed."""


keyring_errors.NoKeyringError = NoKeyringError
keyring_module = types.ModuleType("keyring")
keyring_module.errors = keyring_errors
sys.modules.setdefault("keyring", keyring_module)
sys.modules.setdefault("keyring.errors", keyring_errors)

langgraph_graph = types.ModuleType("langgraph.graph")
langgraph_graph.END = object()



**Code Context (if any):**
{code or "N/A"}

Respond with a JSON object containing two keys:
1. "specialists_needed": A list of specialist names from the available list.
2. "complexity": A string, one of "low", "medium", or "high".

Example:
{{
  "specialists_needed": ["coder", "security"],
  "complexity": "medium"
}}

JSON Response:
"""
        try:
            response_str = await self.mcp_client.generate_response("ollama", "llama3.2", prompt)
            analysis = json.loads(response_str)
            if not isinstance(
                    analysis.get("specialists_needed"),
                    list) or not isinstance(
                    analysis.get("complexity"),
                    str):
                raise ValueError("Invalid JSON structure from analysis model")
            return analysis
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to analyze request complexity: {e}")
            return {"specialists_needed": [], "complexity": "unknown"}

    async def coordinate_specialists(
        self,
        request: str,
        code: str | None = None,
        user_context: str | None = None,
        context: Any | None = None,
        novelty_boost: float = 0.0,
    ) -> Dict[str, Any]:
        """Coordinate multiple specialists to handle complex request."""
        analysis = await self._analyze_request_complexity(request, code)
        analysis["coordination_type"] = self._determine_coordination_type(
            analysis.get("specialists_needed", []), analysis.get(
                "complexity", "unknown")
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

        score = result.get(
            "oracle_score", 1.0 if result.get("type") != "error" else 0.0
        )
        path_memory.record(score)

        review = await self.critic.review(result)
        if review.get("veto"):
            violations = ", ".join(review.get("violations", []))
            return self._create_error_response(
                f"Critic veto: {violations or 'unspecified'}", request
            )
        return result

    async def dispatch_specialist(
        self,
        specialist_type: str,
        task: str,
        *,
        context: Any | None = None,
        user_context: str | None = None,
        models: List[str] | None = None,
        timeout: int = 60,
        retries: int = 3,
    ) -> Dict[str, Any]:
        """Execute a task with the requested specialist.

        The specialist's ``process_task`` method is executed with
        ``asyncio.wait_for`` to enforce the provided timeout. The call is
        retried up to ``retries`` times, logging each failure and aborting
        after the maximum number of retries.
        """
        cache_key = f"{specialist_type}:{task}"
        cached = self.semantic_cache.get(cache_key)
        if cached is not None:
            return cached
        if specialist_type in self.specialists:
            specialist = self.specialists[specialist_type]
            kwargs = {"context": context, "user_context": user_context}
            if models is not None:
                kwargs["models"] = models
            for attempt in range(1, retries + 1):
                try:
                    result = await asyncio.wait_for(
                        specialist.process_task(task, **kwargs), timeout
                    )
                    if not isinstance(
                            result, dict) or "response" not in result:
                        logger.error(
                            "Specialist %s returned incomplete result",
                            specialist_type)
                        # Convert malformed output into a structured error so
                        # downstream coordination can safely ignore it.
                        return self._create_specialist_error(
                            specialist_type, "Invalid or incomplete response"
                        )
                    self.semantic_cache.add(cache_key, result)
                    return result
                except Exception as e:
                    logger.warning(
                        "Attempt %s/%s for %s failed: %s",
                        attempt,
                        retries,
                        specialist_type,
                        e,
                    )
                    if attempt == retries:
                        raise
        if specialist_type in self.child_orchestrators:
            result = await self.run_child_orchestrator(
                specialist_type, task, context=context, user_context=user_context
            )
            self.semantic_cache.add(cache_key, result)
            return result
        raise ValueError(
            f"Unknown specialist or orchestrator: {specialist_type}")

    def create_child_orchestrator(self, name: str, spec: Dict[str, Any]):
        """Create and register a child :class:`SubOrchestrator`."""
        from .sub_orchestrator import SubOrchestrator  # Local import to avoid cycle

        child = SubOrchestrator(self.mcp_client, **spec)
        self.child_orchestrators[name] = child
        return child

    def remove_child_orchestrator(self, name: str) -> bool:
        """Remove a child orchestrator by name."""
        return self.child_orchestrators.pop(name, None) is not None

    def _determine_coordination_type(
            self,
            specialists: List[str],
            complexity: str) -> str:
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

    def _route_model_preferences(
            self,
            specialist,
            complexity: str) -> List[str]:
        """Determine model order based on system resources and task complexity."""
        models = list(specialist.preferred_models)
        local = [
            m for m in models if specialist._get_server_for_model(m) == "ollama"]
        cloud = [
            m for m in models if specialist._get_server_for_model(m) != "ollama"]

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
                "type": "single_specialist",
                "complexity": analysis["complexity"],
                "specialists_used": [specialist_type],
                "results": {
                    specialist_type: result},
                "synthesized_response": result.get(
                    "response",
                    ""),
                "confidence": auction.winner.bid,
                "coordination_summary": f"Auction won by {auction.winner.agent}",
                "auction": {
                    "winner": auction.winner.agent,
                    "price": auction.price},
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
            models = self._route_model_preferences(
                specialist, analysis["complexity"])
            prompt = specialist.build_prompt(task, context, user_context)
            primary_model = models[0]
            server = specialist._get_server_for_model(primary_model)
            grouped[(server, primary_model)].append(
                (specialist_type, specialist, prompt, models))

        try:
            batch_tasks, group_info = [], []
            for (server, model), items in grouped.items():
                prompts = [it[2] for it in items]
                batch_tasks.append(
                    self.mcp_client.generate_response_batch(
                        server, model, prompts))
                group_info.append((server, model, items))

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            specialist_results, successful_results = {}, []
            for (
                    server, model, items), responses in zip(
                    group_info, batch_results):
                if isinstance(responses, Exception):
                    logger.error(f"Batch {server}/{model} failed: {responses}")
                    for stype, _spec, _prompt, mods in items:
                        try:
                            res = await self.dispatch_specialist(
                                stype,
                                task,
                                context=context,
                                user_context=user_context,
                                models=mods,
                            )
                        except Exception as e:
                            res = self._create_specialist_error(stype, str(e))
                        specialist_results[stype] = res
                        if res.get("type") != "error":
                            successful_results.append(res)
                            path_memory.add_decisions(
                                res.get("suggestions", [])[:3])
                    continue

                for (
                        specialist_type, specialist, _, _), response in zip(
                        items, responses):
                    result = specialist.process_model_response(
                        response, model, task)
                    specialist_results[specialist_type] = result
                    if result.get("type") != "error":
                        successful_results.append(result)
                        path_memory.add_decisions(
                            result.get("suggestions", [])[:3])

            candidates = [
                Candidate(
                    agent=res.get("specialist", "unknown"),
                    bid=float(res.get("confidence", 0.0)),
                    content=res.get("response", ""),
                )
                for res in successful_results
            ]
            auction = run_vickrey_auction(candidates) if candidates else None
            if auction:
                self.exploration_stats.append(auction.metrics)

            synthesized_response = await self._synthesize_parallel_results(request, successful_results)
            return {
                "type": "parallel_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": synthesized_response,
                "confidence": auction.winner.bid if auction else 0.0,
                "coordination_summary": f"Auction won by {auction.winner.agent}" if auction else "No winner",
                "auction": {
                    "winner": auction.winner.agent,
                    "price": auction.price} if auction else {},
                "exploration_metrics": auction.metrics if auction else {},
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
                models = self._route_model_preferences(
                    specialist, analysis["complexity"]) if specialist else None

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
                logger.info(
                    f"Completed {specialist_type} analysis, passing context to next specialist")



langgraph_graph.StateGraph = StateGraph
langgraph_module = types.ModuleType("langgraph")
langgraph_module.graph = langgraph_graph
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", langgraph_graph)

return {
                "type": "sequential_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": synthesized_response,
                "confidence": winner_bid,
                "coordination_summary": f"Auction won by {winner_agent} after sequential analysis",
                "auction": {
                    "winner": winner_agent,
                    "price": auction_price},
                "exploration_metrics": auction.metrics if auction else {},
            }
        except Exception as e:
            logger.error(f"Sequential specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)

    def _create_specialist_task(
            self,
            request: str,
            code: str = None,
            user_context: str = None) -> str:
        task_parts = [request]
        if code:
            task_parts.append(f"\n**Code to Analyze:**\n```\n{code}\n```")
        if user_context:
            task_parts.append(f"\n**Additional Context:**\n{user_context}")
        return "\n".join(task_parts)

    async def _synthesize_parallel_results(
            self,
            original_request: str,
            results: List[Dict]) -> str:
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

    async def _synthesize_sequential_results(
            self, original_request: str, results: Dict[str, Dict]) -> str:
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
                synthesis += "**Key Recommendations:**\n" + \
                    "".join(f"- {s}\n" for s in suggestions[:3])
            if issues:
                synthesis += "**Priority Issues:**\n" + \
                    "".join(
                        f"- {i.get('description', 'Unknown')}\n" for i in issues[:2])
            synthesis += "\n"
        synthesis += "**Next Steps:** Review each specialist's recommendations..."
        return synthesis

    def _calculate_overall_confidence(self, results: List[Dict]) -> float:
        if not results:
            return 0.0
        confidences = [r.get("confidence", 0.5) for r in results]
        base_confidence = sum(confidences) / len(confidences)
        if len(results) > 1:
            base_confidence += min(0.1 * (len(results) - 1), 0.3)
        return min(base_confidence, 1.0)

    def _create_simple_response(self, request: str) -> Dict[str, Any]:
        return {
            "type": "simple",
            "complexity": "low",
            "specialists_used": [],
            "results": {},
            "synthesized_response": f"This appears to be a simple request: {request}",
            "confidence": 0.6,
            "coordination_summary": "No specialist coordination needed"}

    def _create_error_response(
            self, error_msg: str, request: str) -> Dict[str, Any]:
        """Return a sanitized error structure for orchestration failures."""

        safe_msg = error_msg.splitlines()[0][:200]
        return {
            "type": "error",
            "complexity": "unknown",
            "specialists_used": [],
            "results": {},
            "synthesized_response": f"I apologize, but I encountered an error: {safe_msg}",
            "confidence": 0.0,
            "error": True,
            "coordination_summary": f"Coordination failed: {safe_msg}",
        }

    def _create_specialist_error(
            self, specialist_type: str, error_msg: str) -> Dict[str, Any]:
        """Return a sanitized error result for a single specialist."""

        safe_msg = error_msg.splitlines()[0][:200]
        return {
            "specialist": specialist_type,
            "response": f"Analysis failed: {safe_msg}",
            "confidence": 0.0,
            "suggestions": [],
            "priority_issues": [],
            "error": True,
            "type": "error",
        }

    orch_stub = types.ModuleType("jarvis.orchestration")
    orch_stub.__path__ = [str(root / "orchestration")]
    monkeypatch.setitem(sys.modules, "jarvis.orchestration", orch_stub)