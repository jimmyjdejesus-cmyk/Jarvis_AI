"""Semantic cache backed by the shared vector store.

The cache hashes requests and stores them alongside their responses. When
``get`` is called, the request text is queried against the project's
vector store and, if a sufficiently similar past request is
found, the associated response is returned. This allows repeated or
near-duplicate requests to bypass expensive specialist execution.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from time import perf_counter
from typing import Any, Callable, Dict, Optional, Tuple

# This assumes a central memory_service is available in your project
from memory_service import vector_store


@dataclass
class SemanticCache:
    """Vector-store-backed semantic cache.

    Parameters
    ----------
    threshold:
        Minimum similarity ratio required for a cache hit. ``SequenceMatcher``
        is used to compare the incoming request with the closest document
        retrieved from the vector store.
    """

    threshold: float = 0.8
    _responses: Dict[str, Any] = field(default_factory=dict)

    def _hash(self, text: str) -> str:
        """Return a stable hash for ``text``."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def add(self, request: str, response: Any) -> None:
        """Add a request/response pair to the cache."""
        key = self._hash(request)
        vector_store.add_text("orchestrator", "semantic_cache", key, request)
        self._responses[key] = response

    def get(self, request: str) -> Optional[Any]:
        """Return cached response when a similar request is found."""
        result = vector_store.query_text(request, n_results=1)
        docs = result.get("documents", [[]])
        if docs and docs[0]:
            candidate = docs[0][0]
            score = SequenceMatcher(None, request, candidate).ratio()
            if score >= self.threshold:
                key = self._hash(candidate)
                return self._responses.get(key)
        return None

    def execute(
        self, request: str, fn: Callable[[], Any]
    ) -> Tuple[Any, bool, float]:
        """Execute ``fn`` with semantic caching.

        Returns a tuple of ``(response, from_cache, duration)`` where
        ``duration`` is in seconds.
        """
        cached = self.get(request)
        if cached is not None:
            return cached, True, 0.0

        start = perf_counter()
        response = fn()
        duration = perf_counter() - start
        self.add(request, response)
        return response, False, duration
