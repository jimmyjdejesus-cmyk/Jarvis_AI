"""Qdrant-backed vector store with basic eviction policy."""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from .config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    VECTOR_SIZE,
    MAX_VECTOR_ENTRIES,
)


def _hash_embedding(text: str) -> List[float]:
    """Return a deterministic embedding for ``text``."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [
        float(int.from_bytes(digest[i * 4:(i + 1) * 4], "big") % 1024)
        for i in range(VECTOR_SIZE)
    ]


class VectorStore:
    """Thin wrapper around Qdrant for text storage and search."""

    def __init__(
        self,
        url: str = QDRANT_URL,
        collection: str = QDRANT_COLLECTION,
        *,
        vector_size: int = VECTOR_SIZE,
        max_entries: int = MAX_VECTOR_ENTRIES,
    ) -> None:
        self.client = QdrantClient(url)
        self.collection = collection
        self.vector_size = vector_size
        self.max_entries = max_entries
        self._ensure_collection()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_collection(self) -> None:
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                self.collection,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )

    def _filter(self, principal: str, scope: str) -> Filter:
        """Build a Qdrant ``Filter`` for ``principal`` and ``scope``."""

        return Filter(
            must=[
                FieldCondition(
                    key="principal", match=MatchValue(value=principal)
                ),
                FieldCondition(key="scope", match=MatchValue(value=scope)),
            ]
        )

    def _enforce_limit(self, principal: str, scope: str) -> None:
        """Cap stored entries for ``principal``/``scope`` at ``max_entries``.

        Older points are removed when the limit is exceeded. Missing
        ``timestamp`` values are treated as the oldest entries.
        """

        flt = self._filter(principal, scope)
        points, _ = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=flt,
            with_payload=True,
            limit=self.max_entries + 1,
        )
        if len(points) > self.max_entries:
            points.sort(key=lambda p: p.payload.get("timestamp", 0))
            ids = [p.id for p in points[:-self.max_entries]]
            self.client.delete(
                collection_name=self.collection, points_selector=ids
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_text(
        self, principal: str, scope: str, key: str, text: str
    ) -> None:
        """Store ``text`` with identifiers for retrieval."""
        vector = _hash_embedding(text)
        payload: Dict[str, str | float] = {
            "principal": principal,
            "scope": scope,
            "key": key,
            "text": text,
            "timestamp": time.time(),
        }
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(id=point_id, vector=vector, payload=payload)
            ],
        )
        self._enforce_limit(principal, scope)

    def query_text(
        self, query: str, n_results: int = 5
    ) -> Dict[str, List[List[str]]]:
        """Return documents semantically similar to ``query``.

        Args:
            query: Input text to search for similar content.
            n_results: Number of documents to return. Must be positive.

        Returns:
            Mapping with a ``documents`` key containing lists of texts.

        Raises:
            ValueError: If ``n_results`` is less than 1.
        """
        if n_results < 1:
            raise ValueError("n_results must be positive")

        vector = _hash_embedding(query)
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=n_results,
        )
        return {
            "documents": [
                [hit.payload.get("text", "") for hit in hits]
            ]
        }

    def evict_scope(self, principal: str, scope: str) -> None:
        """Remove all entries for ``principal`` and ``scope``."""
        flt = self._filter(principal, scope)
        self.client.delete(collection_name=self.collection, filter=flt)
