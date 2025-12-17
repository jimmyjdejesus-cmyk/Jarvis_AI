# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""Structured logging configuration and utilities for Jarvis Core.

This module provides centralized logging configuration for the Jarvis application
with structured JSON output, automatic configuration, and trace-friendly formatting.
It supports both console and file logging with proper handling of extra fields
and exception information.

Key features:
- JSON-formatted structured logging
- Automatic configuration from environment variables
- Support for both console and file handlers
- Proper handling of extra fields and context data
- Singleton configuration pattern to prevent reconfiguration
"""

from __future__ import annotations

import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Global flag to ensure logging is only configured once
_LOGGER_CONFIGURED = False


def configure_logging(log_level: str | int = "INFO", log_path: Optional[str] = None) -> None:
    """Configure central structured logging for the Jarvis runtime.
    
    Sets up JSON-formatted logging with both console and optional file handlers.
    Uses environment variables JARVIS_LOG_LEVEL and JARVIS_LOG_PATH for configuration.
    Implements singleton pattern to prevent multiple configurations.
    
    Args:
        log_level: Logging level (e.g., "INFO", "DEBUG", 20). Defaults to "INFO"
        log_path: Optional path to log file. If provided, enables file logging
        
    Note:
        This function is idempotent - calling it multiple times has no effect
        after the initial configuration.
    """
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return

    # Normalize log level to uppercase string for logging module
    level = log_level
    if isinstance(level, str):
        level = level.upper()

    # Configure handlers - always include console, optionally add file
    handlers: Dict[str, Dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        }
    }

    # Add file handler if log path is specified
    if log_path:
        file_path = Path(log_path).expanduser().resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": str(file_path),
            "encoding": "utf-8",
        }

    # Configure logging system with JSON formatter
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "jarvis_core.logger.JsonFormatter",
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
    """JSON formatter for structured logging with trace-friendly fields.
    
    Formats log records as JSON objects with standard fields (level, logger, message, time)
    plus any extra fields provided via the 'extra' parameter. Exception information
    is included when present. Designed for easy parsing by log aggregation systems.
    
    Key features:
    - Consistent timestamp format (ISO-like)
    - Automatic inclusion of extra fields
    - Exception info serialization
    - Unicode-safe JSON encoding
    """

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - inherits docs
        """Format log record as JSON string.
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON string representation of the log record
        """
        data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
        }
        
        # Include exception information if present
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        
        # Extract and include extra fields that aren't part of standard LogRecord
        # This allows structured logging with custom context data
        standard_attrs = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        for key, value in record.__dict__.items():
            if key not in standard_attrs and key not in data:
                data[key] = value
                
        return json.dumps(data, ensure_ascii=False)


def get_logger(name: str = "jarvis") -> logging.Logger:
    """Get a module-level logger configured for the Jarvis runtime.
    
    Automatically configures logging if not already done, using environment
    variables for configuration. Returns a logger instance configured with
    JSON formatting and appropriate handlers.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        
    Returns:
        Configured logger instance with JSON formatting
        
    Environment Variables:
        JARVIS_LOG_LEVEL: Logging level (default: "INFO")
        JARVIS_LOG_PATH: Optional path to log file
    """
    if not _LOGGER_CONFIGURED:
        configure_logging(os.getenv("JARVIS_LOG_LEVEL", "INFO"), os.getenv("JARVIS_LOG_PATH"))
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger", "JsonFormatter"]
