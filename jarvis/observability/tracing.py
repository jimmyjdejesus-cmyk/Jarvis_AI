"""Optional LangSmith tracing hooks."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    from langsmith import Client
except Exception:  # LangSmith is optional
    Client = None  # type: ignore

_client: Optional[Client] = None


def _get_client() -> Client:
    global _client
    if _client is None:
        if Client is None:
            raise RuntimeError("langsmith is not installed")
        _client = Client()
    return _client


@contextmanager
def trace(name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager creating a LangSmith trace if the package is installed."""

    if Client is None:
        yield None
        return

    client = _get_client()
    run = client.create_run(name=name, inputs={}, metadata=metadata or {})
    try:
        yield run
    finally:
        try:
            client.end_run(run["id"] if isinstance(run, dict) else run.id)
        except Exception:
            pass
