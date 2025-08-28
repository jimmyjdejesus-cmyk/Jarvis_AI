"""Route curiosity questions into mission directive queue."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover - optional redis dependency
    from jarvis.orchestration.task_queue import RedisTaskQueue
except (ImportError, SyntaxError):  # pragma: no cover - fallback for tests without redis

    class RedisTaskQueue:  # type: ignore
        """Fallback in-memory queue used when Redis is unavailable."""

        def __init__(self, *args: any, **kwargs: any) -> None:  # pragma: no cover - test stub
            self.items: list[dict] = []

        def enqueue(self, task: dict) -> None:  # pragma: no cover - test stub
            self.items.append(task)


@dataclass
class CuriosityRouter:
    """Route curiosity questions into sanitized mission directives.

    The router prepends a short prefix and strips potentially unsafe
    characters to reduce the risk of injecting unintended commands.
    """

    prefix: str = "Investigate"
    queue: Optional[RedisTaskQueue] = None
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.queue:
            self.queue = RedisTaskQueue(name="curiosity_directives")

    def route(self, question: str) -> None:
        """Enqueue `question` as a mission directive if routing is enabled."""
        if not self.enabled:
            return
        cleaned = re.sub(r"[\r\n;]+", " ", question).strip().rstrip("?")
        directive = f"{self.prefix}: {cleaned}"
        task = {"type": "directive", "request": directive}
        self.queue.enqueue(task)

__all__ = ["CuriosityRouter"]