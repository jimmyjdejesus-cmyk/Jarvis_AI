from __future__ import annotations

import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict, Optional

_LOGGER_CONFIGURED = False


def configure_logging(log_level: str | int = "INFO", log_path: Optional[str] = None) -> None:
    """Configure a central structured logger for the Jarvis runtime."""
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return

    level = log_level
    if isinstance(level, str):
        level = level.upper()

    handlers: Dict[str, Dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        }
    }

    if log_path:
        file_path = Path(log_path).expanduser().resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": str(file_path),
            "encoding": "utf-8",
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "jarvis_core.logging.JsonFormatter",
                }
            },
            "handlers": handlers,
            "root": {
                "level": level,
                "handlers": list(handlers.keys()),
            },
        }
    )
    _LOGGER_CONFIGURED = True


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter with trace-friendly fields."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - inherits docs
        data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
        }
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        # The `extra` dict is merged into the record's __dict__.
        # This part captures all extra fields by finding keys that are not standard.
        standard_attrs = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        for key, value in record.__dict__.items():
            if key not in standard_attrs and key not in data:
                data[key] = value
        return json.dumps(data, ensure_ascii=False)


def get_logger(name: str = "jarvis") -> logging.Logger:
    """Get a module-level logger configured for the Jarvis runtime."""
    if not _LOGGER_CONFIGURED:
        configure_logging(os.getenv("JARVIS_LOG_LEVEL", "INFO"), os.getenv("JARVIS_LOG_PATH"))
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger", "JsonFormatter"]
