"""Semantic cache for reusing similar requests.

Caches request-response pairs with simple similarity matching
using ``difflib.SequenceMatcher``. When a new request is
encountered, the cache searches for the most similar previous
request. If the similarity ratio exceeds a configurable
threshold, the cached response is returned.

This provides a lightweight semantic memoization mechanism that
can significantly reduce latency for repeated or near-duplicate
requests.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from time import perf_counter
from typing import Callable, List, Optional, Tuple


@dataclass
class CacheEntry:
    """Stored request/response pair."""

    request: str
    response: str


@dataclass
class SemanticCache:
    """Simple in-memory semantic cache.

    Parameters
    ----------
    threshold:
        Minimum similarity ratio required for a cache hit. The ratio is
        computed using ``difflib.SequenceMatcher`` and ranges from 0.0 to 1.0.
    """

    threshold: float = 0.8
    _entries: List[CacheEntry] = field(default_factory=list)

    def add(self, request: str, response: str) -> None:
        """Add a request/response pair to the cache."""

        self._entries.append(CacheEntry(request=request, response=response))

    def get(self, request: str) -> Optional[str]:
        """Return cached response when similarity exceeds the threshold."""

        best_score = 0.0
        best_response: Optional[str] = None
        for entry in self._entries:
            score = SequenceMatcher(None, request, entry.request).ratio()
            if score > best_score:
                best_score = score
                best_response = entry.response
        if best_score >= self.threshold:
            return best_response
        return None

    def execute(
        self, request: str, fn: Callable[[], str]
    ) -> Tuple[str, bool, float]:
        """Execute ``fn`` with semantic caching.

        Parameters
        ----------
        request:
            Text describing the request.
        fn:
            Function that produces the response if cache miss occurs.

        Returns
        -------
        tuple
            ``(response, from_cache, duration)`` where ``duration`` is the
            execution time in seconds.
        """

        cached = self.get(request)
        if cached is not None:
            return cached, True, 0.0

        start = perf_counter()
        response = fn()
        duration = perf_counter() - start
        self.add(request, response)
        return response, False, duration
