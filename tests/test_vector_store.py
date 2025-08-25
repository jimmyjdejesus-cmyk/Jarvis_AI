import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from memory_service.vector_store import (  # noqa: E402
    add_text,
    query_text,
    delete_text,
)


def test_vector_store_basic_operations():
    add_text("user", "scope", "key", "hello world")
    result = query_text("hello")
    assert "hello world" in result["documents"][0]
    delete_text("user", "scope", "key")
    result = query_text("hello")
    assert result["documents"][0] == []
