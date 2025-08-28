"""Route curiosity questions into a persistent task queue."""

from __future__ import annotations

import json
import logging
import re
import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, Optional

try:  # pragma: no cover - optional redis dependency
    import redis
except Exception:  # pragma: no cover - redis is optional for testing
    redis = None


logger = logging.getLogger(__name__)


class PersistentQueue:
    """Redis-backed queue with in-memory fallback and thread safety.

    The queue attempts to use Redis for durability. If Redis is not
    available or a connection failure occurs, it transparently falls back
    to an in-memory deque protected by a lock so it remains safe under
    concurrent access.
    """

    def __init__(
        self,
        name: str = "curiosity_directives",
        client: Optional["redis.Redis"] = None,
    ) -> None:
        self.name = name
        self._lock = threading.Lock()
        if client is not None:
            self.client = client
        elif redis is not None:
            self.client = redis.Redis(
                host="localhost", port=6379, db=0, decode_responses=True
            )
        else:  # pragma: no cover - redis not installed
            self.client = None
        self._local: Deque[Dict[str, Any]] = deque()

    def enqueue(self, task: Dict[str, Any]) -> None:
        """Add ``task`` to the queue.

        If Redis is unavailable or a connection error occurs, the task is
        stored in an in-memory deque so that the calling code does not
        raise. This behaviour ensures curiosity routing does not fail hard
        when the persistence layer is unreachable.
        """

        try:
            if self.client is not None:
                self.client.rpush(self.name, json.dumps(task))
                return
        except Exception as exc:  # pragma: no cover - network failure
            logger.warning(
                "Redis enqueue failed, using in-memory queue: %s", exc
            )

        with self._lock:
            self._local.append(task)

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Retrieve the next task from the queue if available."""

        # Drain any locally queued items first so tasks enqueued while Redis
        # was unreachable are not starved once connectivity returns.
        with self._lock:
            if self._local:
                return self._local.popleft()

        try:
            if self.client is not None:
                data = self.client.lpop(self.name)
                if data:
                    return json.loads(data)
        except Exception as exc:  # pragma: no cover - network failure
            logger.warning(
                "Redis dequeue failed, falling back to memory: %s", exc
            )

        with self._lock:
            return self._local.popleft() if self._local else None


@dataclass
class CuriosityRouter:
    """Route curiosity questions into sanitized mission directives."""

    prefix: str = "Investigate"
    queue: Optional[PersistentQueue] = None
    enabled: bool = True

    def __post_init__(self) -> None:  # pragma: no cover - simple assignment
        if self.queue is None:
            self.queue = PersistentQueue()

    def route(self, question: str) -> None:
        """Enqueue ``question`` as a mission directive when enabled."""

        if not self.enabled:
            return
        cleaned = re.sub(r"[\r\n;]+", " ", question).strip().rstrip("?")
        directive = f"{self.prefix}: {cleaned}"
        task = {"type": "directive", "request": directive}
        self.queue.enqueue(task)


__all__ = ["CuriosityRouter", "PersistentQueue"]
