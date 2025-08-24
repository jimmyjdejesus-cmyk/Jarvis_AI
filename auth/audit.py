"""Simple audit logging utilities."""

from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime

_log_path = Path("audit.log")
_logger = logging.getLogger("audit")
_handler = logging.FileHandler(_log_path)
_logger.addHandler(_handler)
_logger.setLevel(logging.INFO)


def log_action(user: str, action: str) -> None:
    """Write an audit entry identifying who performed an action."""
    timestamp = datetime.utcnow().isoformat()
    _logger.info("%s|%s|%s", timestamp, user, action)


__all__ = ["log_action"]
