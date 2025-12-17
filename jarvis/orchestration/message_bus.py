# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations
import asyncio
from typing import Any


class HierarchicalMessageBus:
    """A minimal hierarchical message bus for tests.

    The production implementation would publish messages to monitoring/observability
    layers and downstream consumers. For unit tests and local runs, we implement a
    no-op async `publish` method that collects messages in memory if needed for
    debugging.
    """
    def __init__(self) -> None:
        self._messages: list[tuple[str, Any]] = []

    async def publish(self, event: str, payload: Any, run_id: str | None = None, step_id: str | None = None, parent_id: str | None = None) -> None:
        # Simple asynchronous no-op that stores messages locally for introspection
        self._messages.append((event, payload))
        await asyncio.sleep(0)  # yield control

    def get_messages(self) -> list[tuple[str, Any]]:
        return list(self._messages)
