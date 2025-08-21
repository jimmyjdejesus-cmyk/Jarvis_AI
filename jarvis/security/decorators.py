"""Decorators for enforcing rate limits and timeouts."""

from __future__ import annotations

import asyncio
import concurrent.futures
import functools
import threading
import time
from collections import deque
from typing import Any, Callable, Deque


def rate_limit(calls: int, period: float) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Rate limit decorator for both sync and async functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        timestamps: Deque[float] = deque()
        lock = threading.Lock()
        async_lock = asyncio.Lock()

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            async with async_lock:
                _enforce_rate_limit(timestamps, period, calls)
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with lock:
                _enforce_rate_limit(timestamps, period, calls)
            return func(*args, **kwargs)

        def _enforce_rate_limit(times: Deque[float], per: float, max_calls: int) -> None:
            now = time.monotonic()
            while times and now - times[0] > per:
                times.popleft()
            if len(times) >= max_calls:
                raise RuntimeError("Rate limit exceeded")
            times.append(now)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def timeout(seconds: float) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Timeout decorator for both sync and async functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result(timeout=seconds)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
