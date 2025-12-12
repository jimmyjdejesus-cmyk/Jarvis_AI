"""Tiny shim for PyYAML's safe_load used in legacy code during tests.

This is intentionally minimal and returns an empty dict for missing/empty
input; it avoids adding PyYAML as a heavy dependency for CI collection.
"""

from typing import Any, IO


def safe_load(stream: IO | str | None) -> Any:
    # Accept file-like object or string; return empty mapping when not present.
    if stream is None:
        return {}
    try:
        if hasattr(stream, "read"):
            data = stream.read()
        else:
            data = str(stream)
        if not data.strip():
            return {}
        # Very small heuristic: if it looks like JSON, parse it; else return {}
        import json

        try:
            return json.loads(data)
        except Exception:
            return {}
    except Exception:
        return {}
