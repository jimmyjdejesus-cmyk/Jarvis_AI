from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jarvis.memory.client import ACLViolation, MemoryClient
from memory_service import EVENTS, app


@pytest.fixture(autouse=True)
def clear_events() -> None:
    EVENTS.clear()


def test_memory_acl_and_events() -> None:
    client = TestClient(app)
    mclient = MemoryClient(
        base_url=str(client.base_url),
        principal="alice",
        allowed_scopes={"notes"},
        http_client=client,
    )

    # Allowed write/read
    mclient.write("notes", "greeting", "hello")
    assert mclient.read("notes", "greeting") == "hello"
    assert len(EVENTS) == 2  # write + read

    # Hashing returns deterministic value
    digest = mclient.scope_hash("notes")
    assert isinstance(digest, str) and len(digest) == 64
    assert EVENTS[-1]["type"] == "hash"

    # ACL enforcement
    with pytest.raises(ACLViolation):
        mclient.write("secret", "key", "value")

    # Ensure WS7 version tag present in all events
    assert all(event.get("version") == "WS7" for event in EVENTS)


def test_filesystem_access_blocked() -> None:
    with pytest.raises(ValueError):
        MemoryClient("file:///tmp", "bob", ["any"])
