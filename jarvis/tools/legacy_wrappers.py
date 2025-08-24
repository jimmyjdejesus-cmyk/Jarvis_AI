"""Wrappers for legacy environment tools.

This module provides thin wrappers around the old environment tools in order to
normalise their input/output behaviour and to enforce a simple filesystem
allow/deny list policy.  The wrappers return dictionaries with ``ok`` and
``result``/``error`` fields so that callers can interact with a consistent API.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

from .environment_tools import (
    read_file as _legacy_read_file,
    write_file as _legacy_write_file,
    run_shell_command as _legacy_run_shell,
)

# ---------------------------------------------------------------------------
# Filesystem policy configuration
# ---------------------------------------------------------------------------
ALLOWED_PATHS: Iterable[Path] = [Path.cwd()]
DENIED_PATHS: Iterable[Path] = []


def set_filesystem_policy(
    allow: Optional[Iterable[str]] = None, deny: Optional[Iterable[str]] = None
) -> None:
    """Configure allow/deny lists for filesystem access."""

    global ALLOWED_PATHS, DENIED_PATHS
    if allow is not None:
        ALLOWED_PATHS = [Path(p).resolve() for p in allow]
    if deny is not None:
        DENIED_PATHS = [Path(p).resolve() for p in deny]


def _check_path(path: str) -> Path:
    """Validate a path against the allow/deny lists."""

    p = Path(path).resolve()
    for denied in DENIED_PATHS:
        if str(p).startswith(str(denied)):
            raise PermissionError(f"Access to {p} denied")
    if ALLOWED_PATHS and not any(str(p).startswith(str(a)) for a in ALLOWED_PATHS):
        raise PermissionError(f"Access to {p} not allowed")
    return p


def _wrap_io(fn: Callable[..., Any]) -> Callable[..., Dict[str, Any]]:
    """Normalise tool output into a dictionary."""

    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            return {"ok": True, "result": result}
        except Exception as exc:  # pragma: no cover - defensive
            return {"ok": False, "error": str(exc)}

    return wrapper


@_wrap_io
def safe_read_file(path: str, username: str = "unknown"):
    checked = _check_path(path)
    return _legacy_read_file(str(checked), username)


@_wrap_io
def safe_write_file(path: str, content: str, username: str = "unknown"):
    checked = _check_path(path)
    return _legacy_write_file(str(checked), content, username)


@_wrap_io
def safe_run_shell_command(command: str, username: str = "unknown"):
    return _legacy_run_shell(command, username)


__all__ = [
    "safe_read_file",
    "safe_write_file",
    "safe_run_shell_command",
    "set_filesystem_policy",
]

