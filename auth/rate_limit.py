"""Simple in-memory rate limiting utilities."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass


@dataclass
class RateLimiter:
    """Allow ``max_calls`` within ``period`` seconds."""

    max_calls: int
    period: float

    def __post_init__(self) -> None:
        self.calls: deque[float] = deque()

    def allow(self) -> bool:
        now = time.monotonic()
        while self.calls and now - self.calls[0] > self.period:
            self.calls.popleft()
        if len(self.calls) >= self.max_calls:
            return False
        self.calls.append(now)
        return True


__all__ = ["RateLimiter"]
