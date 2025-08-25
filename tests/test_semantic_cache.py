import importlib.util
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "jarvis" / "orchestration" / "semantic_cache.py"
spec = importlib.util.spec_from_file_location("semantic_cache", MODULE_PATH)
semantic_cache = importlib.util.module_from_spec(spec)
sys.modules["semantic_cache"] = semantic_cache
spec.loader.exec_module(semantic_cache)  # type: ignore
SemanticCache = semantic_cache.SemanticCache


def slow_fn():
    time.sleep(0.2)
    return "ok"


def test_cache_reduces_latency():
    cache = SemanticCache()

    start = time.perf_counter()
    result, hit, first_duration = cache.execute("request", slow_fn)
    first_elapsed = time.perf_counter() - start

    assert result == "ok"
    assert not hit

    start = time.perf_counter()
    result2, hit2, second_duration = cache.execute("request", slow_fn)
    second_elapsed = time.perf_counter() - start

    assert result2 == "ok"
    assert hit2
    # ensure semantic cache hit is much faster
    assert second_duration <= first_duration * 0.7
    # also ensure observed elapsed times show reduction
    assert second_elapsed <= first_elapsed * 0.7
