"""Minimal JarvisAgentV2 implementation used for testing and examples."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict


class JarvisAgentV2:
    """A tiny placeholder agent used in tests.

    The real project replaces this with a fully featured agent.  The stub
    implementation here merely echoes queries and yields a trivial event
    stream so that the API server and tests can operate without the full
    dependency stack.
    """

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}

    # ------------------------------------------------------------------
    def setup_workflow(self) -> None:  # pragma: no cover - placeholder
        """Prepare the workflow."""

    # ------------------------------------------------------------------
    def run_workflow(self, query: str) -> Dict[str, Any]:
        """Return a minimal response for the given query."""

        return {"query": query, "result": "ok"}

    # ------------------------------------------------------------------
    async def stream_workflow(self, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield a single fake event for streaming tests."""

        yield {"step": "start", "query": query}


__all__ = ["JarvisAgentV2"]
