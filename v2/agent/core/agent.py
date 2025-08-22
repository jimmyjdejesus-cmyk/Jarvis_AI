"""Minimal JarvisAgentV2 implementation used for testing and examples."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict

from v2.config.config import DEFAULT_CONFIG
from jarvis.logging.logger import get_logger


class JarvisAgentV2:
    """A tiny placeholder agent used in tests.

    The real project replaces this with a fully featured agent.  The stub
    implementation here merely echoes queries and yields a trivial event
    stream so that the API server and tests can operate without the full
    dependency stack.
    """

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        """Initialize the agent with configuration and logging."""

        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

        self.logger = get_logger()
        self.logger.info("JarvisAgentV2 initialized.")

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

    # ------------------------------------------------------------------
    async def handle_request(
        self, request: str, code: str | None = None, user_context: str | None = None
    ) -> Dict[str, Any]:
        """Primary entrypoint for handling agent requests."""

        self.logger.info(f"Handling request: {request}")
        return {"request": request, "status": "ok"}


__all__ = ["JarvisAgentV2"]
