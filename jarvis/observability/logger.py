"""Simple structured logging with correlation IDs.

Logs are written as JSON Lines to ``logs/events.jsonl`` while a human friendly
console output is emitted to stdout.  A correlation identifier can be bound to
the current context and is automatically included with each log record.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

# Path to the JSONL log file
EVENT_LOG_PATH = "logs/events.jsonl"

# Context variable storing current correlation id
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def set_correlation_id(value: Optional[str] = None) -> str:
    """Bind a correlation id to the current context.

    Parameters
    ----------
    value: Optional[str]
        Explicit correlation id.  When omitted a new UUID4 value is generated.

    Returns
    -------
    str
        The correlation id bound to the context.
    """

    if value is None:
        value = str(uuid.uuid4())
    _correlation_id.set(value)
    return value


def get_correlation_id() -> Optional[str]:
    """Return the correlation id bound to the current context."""

    return _correlation_id.get()


class _JsonlHandler(logging.Handler):
    """Logging handler writing events as JSON lines."""

    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - simple IO
        event: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
        }
        if getattr(record, "event_type", None):
            event["event_type"] = record.event_type
        if getattr(record, "data", None) is not None:
            event["data"] = record.data
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")


class _ConsoleFormatter(logging.Formatter):
    """Pretty console formatter including correlation ids."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - trivial
        cid = getattr(record, "correlation_id", "-")
        return f"[{record.levelname}] ({cid}) {record.getMessage()}"


def _configure_logger() -> logging.Logger:
    logger = logging.getLogger("jarvis")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    json_handler = _JsonlHandler(EVENT_LOG_PATH)
    console_handler: logging.Handler
    try:  # Prefer Rich console output when available
        from rich.logging import RichHandler

        console_handler = RichHandler(rich_tracebacks=False, markup=False)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
    except Exception:  # pragma: no cover - optional dependency
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(_ConsoleFormatter())

    class _CorrelationFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.correlation_id = get_correlation_id()
            return True

    for h in (json_handler, console_handler):
        h.addFilter(_CorrelationFilter())
        logger.addHandler(h)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger instance."""

    logger = _configure_logger()
    return logger if name in (None, "jarvis") else logger.getChild(name)


def load_events(correlation_id: Optional[str] = None) -> Iterable[dict[str, Any]]:
    """Load events from the JSONL log file.

    Parameters
    ----------
    correlation_id: Optional[str]
        When provided, only events matching this correlation id are yielded.
    """

    if not os.path.exists(EVENT_LOG_PATH):
        return []
    events = []
    with open(EVENT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if correlation_id and event.get("correlation_id") != correlation_id:
                continue
            events.append(event)
    return events
