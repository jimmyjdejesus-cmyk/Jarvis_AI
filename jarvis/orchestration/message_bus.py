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
from typing import Any, Awaitable, Callable, Dict, List, Optional

try:
    from .bandwidth_channel import BandwidthLimitedChannel
except Exception:  # pragma: no cover - allow direct module import
    from bandwidth_channel import BandwidthLimitedChannel

from pydantic import BaseModel, Field


EventHandler = Callable[[Dict[str, Any]], Awaitable[None] | None]


class Event(BaseModel):
    """Schema for events passed through the message bus."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    payload: Any
    scope: str = "global"
    run_id: Optional[str] = None
    step_id: Optional[str] = None
    parent_id: Optional[str] = None
    log: Optional[str] = None


class MessageBus:
    """In-memory pub/sub message bus with scoped event storage."""

    def __init__(self, channel: Optional[BandwidthLimitedChannel] = None) -> None:
        # Mapping of event name to subscribers
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        # Scoped memory of published events
        self._memory: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # Optional communication channel enforcing bandwidth penalties
        self._channel = channel

    def subscribe(self, event: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        self._subscribers[event].append(handler)

    async def publish(
        self,
        event: str,
        payload: Any,
        *,
        scope: str = "global",
        run_id: Optional[str] = None,
        step_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        log: Optional[str] = None,
    ) -> str:
        """Publish an event to all subscribers.

        Parameters
        ----------
        event:
            Event type/name.
        payload:
            Arbitrary JSON‑serialisable payload.
        scope:
            Optional scope identifier used for routing and event history.
        run_id:
            Identifier for the overall run this event belongs to.
        step_id:
            Identifier for the specific step generating the event.
        parent_id:
            Identifier for the parent step that spawned this action.
        log:
            Optional log excerpt associated with the event.

        Returns
        -------
        str
            The unique ID assigned to the published event.
        """
        message = Event(
            type=event,
            payload=payload,
            scope=scope,
            run_id=run_id or scope,
            step_id=step_id,
            parent_id=parent_id,
            log=log,
        )
        self._memory[scope].append(message.model_dump())

        if self._channel is not None:
            await self._channel.transmit(message.model_dump())

        for handler in list(self._subscribers.get(event, [])):
            if asyncio.iscoroutinefunction(handler):
                await handler(message.model_dump())
            else:  # pragma: no cover - simple sync handler
                handler(message.model_dump())
        return message.id

    def get_scope_events(self, scope: str) -> List[Dict[str, Any]]:
        """Return all events published within a given scope."""
        return list(self._memory.get(scope, []))


class HierarchicalMessageBus(MessageBus):
    """Message bus supporting hierarchical topic routing.

    Subscribers can register for a specific topic (e.g. ``"team.dev"``) and
    will receive events published to that topic or any of its descendants
    (``"team.dev.coder"``).  Handlers registered under ``"*"`` receive all
    events regardless of topic.
    """

    async def publish(
        self,
        event: str,
        payload: Any,
        *,
        scope: str = "global",
        run_id: Optional[str] = None,
        step_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        log: Optional[str] = None,
    ) -> str:
        message = Event(
            type=event,
            payload=payload,
            scope=scope,
            run_id=run_id or scope,
            step_id=step_id,
            parent_id=parent_id,
            log=log,
        )
        self._memory[scope].append(message.model_dump())

        handlers: List[EventHandler] = []
        parts = event.split(".")
        for i in range(len(parts), 0, -1):
            prefix = ".".join(parts[:i])
            handlers.extend(self._subscribers.get(prefix, []))
        handlers.extend(self._subscribers.get("*", []))

        # Deduplicate while preserving order
        seen: List[EventHandler] = []
        unique_handlers = []
        for h in handlers:
            if h not in seen:
                seen.append(h)
                unique_handlers.append(h)

        for handler in unique_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(message.model_dump())
            else:  # pragma: no cover - simple sync handler
                handler(message.model_dump())
        return message.id
