"""Lightweight in-memory message bus used for agent coordination.

The bus implements a simple publish/subscribe mechanism.  Each published
message receives a unique event ID and can optionally be associated with a
*scope*.  Events are retained in memory grouped by their scope which allows
components to query the history of a particular mission or conversation.
"""
from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List


EventHandler = Callable[[Dict[str, Any]], Awaitable[None] | None]


class MessageBus:
    """In-memory pub/sub message bus with scoped event storage."""

    def __init__(self) -> None:
        # Mapping of event name to subscribers
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        # Scoped memory of published events
        self._memory: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        self._subscribers[event].append(handler)

    async def publish(self, event: str, payload: Any, scope: str = "global") -> str:
        """Publish an event to all subscribers.

        Parameters
        ----------
        event:
            Event type/name.
        payload:
            Arbitrary JSON‑serialisable payload.
        scope:
            Optional scope identifier used for routing and event history.

        Returns
        -------
        str
            The unique ID assigned to the published event.
        """
        event_id = str(uuid.uuid4())
        message = {"id": event_id, "type": event, "payload": payload, "scope": scope}
        self._memory[scope].append(message)

        for handler in list(self._subscribers.get(event, [])):
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:  # pragma: no cover - simple sync handler
                handler(message)
        return event_id

    def get_scope_events(self, scope: str) -> List[Dict[str, Any]]:
        """Return all events published within a given scope."""
        return list(self._memory.get(scope, []))
