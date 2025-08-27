"""Ensure SemanticCache avoids recomputation."""

import importlib.util
from pathlib import Path
import sys

import memory_service

spec = importlib.util.spec_from_file_location(
    "semantic_cache", Path("jarvis/orchestration/semantic_cache.py")
)
module = importlib.util.module_from_spec(spec)
sys.modules["semantic_cache"] = module
assert spec.loader is not None
spec.loader.exec_module(module)
SemanticCache = module.SemanticCache


def test_execute_uses_cache() -> None:
    # Use a fresh in-memory vector store
    memory_service.vector_store = memory_service.vector_store.__class__()
    cache = SemanticCache()
    calls = {"count": 0}

    def fn() -> str:
        calls["count"] += 1
        return "answer"

    result, from_cache, _ = cache.execute("question", fn)
    assert result == "answer" and not from_cache

    result, from_cache, _ = cache.execute("question", fn)
    assert result == "answer" and from_cache
    assert calls["count"] == 1
