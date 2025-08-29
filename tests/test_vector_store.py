"""Tests for the Qdrant-backed VectorStore."""

import importlib
import sys
import pytest

pytest.importorskip("qdrant_client")

# Remove pre-existing memory_service stubs if present
if "memory_service" in sys.modules and not getattr(sys.modules["memory_service"], "__file__", None):
    sys.modules.pop("memory_service", None)
    sys.modules.pop("memory_service.models", None)

from qdrant_client.models import FieldCondition, Filter, MatchValue
from memory_service.vector_store import VectorStore


def test_add_and_query_text() -> None:
    store = VectorStore()
    store.add_text("user", "scope", "1", "hello world")
    result = store.query_text("hello world", n_results=1)
    assert result["documents"][0][0] == "hello world"


def test_eviction() -> None:
    store = VectorStore(max_entries=1)
    store.add_text("p", "s", "1", "first")
    store.add_text("p", "s", "2", "second")
    flt = Filter(must=[
        FieldCondition(key="principal", match=MatchValue(value="p")),
        FieldCondition(key="scope", match=MatchValue(value="s")),
    ])
    points, _ = store.client.scroll(
        collection_name=store.collection,
        scroll_filter=flt,
        with_payload=True,
    )
    assert len(points) == 1
    assert points[0].payload["text"] == "second"


def test_evict_scope() -> None:
    store = VectorStore()
    store.add_text("p", "s", "1", "first")
    store.add_text("p", "s", "2", "second")
    store.evict_scope("p", "s")
    flt = Filter(
        must=[
            FieldCondition(key="principal", match=MatchValue(value="p")),
            FieldCondition(key="scope", match=MatchValue(value="s")),
        ]
    )
    points, _ = store.client.scroll(
        collection_name=store.collection,
        scroll_filter=flt,
        with_payload=True,
    )
    assert points == []
