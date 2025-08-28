"""Minimal multi-agent orchestrator used in unit tests.

This module intentionally provides lightweight stand‑ins for the full
Jarvis orchestration system so that the test suite can run without the
heavy optional dependencies present in production.  Only the features
exercised by the tests are implemented.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Optional

END = object()


logger = logging.getLogger(__name__)


@dataclass
class AgentSpec:
    """Specification for a specialist agent.

    Attributes
    ----------
    name:
        Identifier for the specialist.
    fn:
        Callable executed for the specialist.
    entry:
        Whether this specialist is an entry point in a workflow.
    """

    name: str
    fn: Callable[..., Awaitable[Any]]
    entry: bool = False


@dataclass
class StepContext:
    """Context information for running a single mission step."""

    request: str
    retry_policy: Dict[str, float] = field(default_factory=dict)
    timeout: Optional[float] = None


@dataclass
class StepResult:
    """Container for step execution results."""

    data: Dict[str, Any]
    error: bool = False


class ConstitutionalCritic:
    """Simplified critic used to approve or veto plans."""
    async def review(self, plan: str) -> Dict[str, Any]:  # pragma: no cover
        return {"veto": False, "violations": []}


class OrchestratorTemplate:
    """Base class placeholder for more advanced orchestrators."""


class DynamicOrchestrator(OrchestratorTemplate):
    """Placeholder that mirrors the production dynamic orchestrator."""


class MultiAgentOrchestrator(DynamicOrchestrator):
    """Coordinate specialist agents to answer a request."""

    def __init__(
        self,
        mcp_client: Any,
        *,
        specialists: Optional[Dict[str, Any]] = None,
        performance_tracker: Any | None = None,
        critic: Any | None = None,
        **_: Any,
    ) -> None:
        self.mcp_client = mcp_client
        self.specialists = specialists or {}
        self.performance_tracker = performance_tracker
        self.critic = critic or ConstitutionalCritic()
        self.child_orchestrators: Dict[str, "MultiAgentOrchestrator"] = {}

    # ------------------------------------------------------------------
    # Specialist coordination
    # ------------------------------------------------------------------
    async def coordinate_specialists(self, request: str) -> Dict[str, Any]:
        """Send ``request`` to the MCP client and apply critic review."""

        review = await self.critic.review(request)
        if review.get("veto"):
            msg = "; ".join(review.get("violations", []))
            return {"error": True, "synthesized_response": msg}

        response = await self.mcp_client.generate_response(None, None, request)
        return {
            "synthesized_response": response,
            "specialists_used": list(self.specialists),
        }

    async def dispatch_specialist(
        self, name: str, task: str, *, timeout: float = 0.05, retries: int = 3
    ) -> Dict[str, Any]:
        """Dispatch a specialist with retry and timeout handling.

        The implementation is intentionally conservative: it attempts the
        specialist call ``retries`` times and raises an exception if all
        attempts fail or do not yield a usable response.
        """

        specialist = self.specialists.get(name) or self.specialists.get(
            name.replace("_", "")
        )
        if specialist is None:
            raise Exception(f"Unknown specialist: {name}")

        last_exc: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                return await asyncio.wait_for(
                    specialist.process_task(task), timeout=timeout
                )
            except Exception as exc:  # pragma: no cover - network/timeout
                last_exc = exc
                logger.warning(
                    "Attempt %d/%d for %s failed", attempt, retries, name
                )
        raise last_exc  # pragma: no cover - propagate last error

    def create_child_orchestrator(
        self, name: str, context: Dict[str, Any]
    ) -> "MultiAgentOrchestrator":
        """Create and store a child orchestrator for hierarchical missions."""

        child = self.__class__(
            self.mcp_client, performance_tracker=self.performance_tracker
        )
        self.child_orchestrators[name] = child
        return child

    async def run_step(self, step_ctx: StepContext) -> StepResult:
        """Execute a step with retry/backoff semantics."""

        retries = step_ctx.retry_policy.get("retries", 0)
        backoff = step_ctx.retry_policy.get("backoff_base", 0)
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            try:
                coro = self.coordinate_specialists(step_ctx.request)
                if step_ctx.timeout:
                    data = await asyncio.wait_for(
                        coro, timeout=step_ctx.timeout
                    )
                else:
                    data = await coro
                return StepResult(data=data)
            except Exception as exc:
                last_exc = exc
                if self.performance_tracker:
                    self.performance_tracker.metrics.setdefault(
                        "failed_steps", 0
                    )
                    self.performance_tracker.metrics["failed_steps"] += 1
                if attempt == retries:
                    raise
                await asyncio.sleep(backoff)
        raise last_exc  # pragma: no cover - defensive


__all__ = [
    "AgentSpec",
    "DynamicOrchestrator",
    "MultiAgentOrchestrator",
    "OrchestratorTemplate",
    "StepContext",
    "StepResult",
    "END",
]
