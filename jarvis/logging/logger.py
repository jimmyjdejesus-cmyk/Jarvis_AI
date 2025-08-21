"""Structured logging configuration for Jarvis.

The :func:`configure` function sets up `structlog` with sensible defaults
that write JSON logs to a local file while also emitting them to stdout.
An optional ``remote_url`` parameter can be provided to forward log events
to an external HTTP endpoint.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import requests
import structlog


def configure(
    log_file: str = "logs/jarvis.log",
    remote_url: Optional[str] = None,
) -> None:
    """Configure global logging behaviour.

    Parameters
    ----------
    log_file:
        Path to the file where logs will be stored. The directory is created
        if it does not already exist.
    remote_url:
        Optional HTTP endpoint that will receive log events as JSON payloads.
        Errors while sending remote logs are silently ignored.
    """

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    handlers = [logging.FileHandler(log_file), logging.StreamHandler()]
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=handlers,
    )

    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if remote_url:

        def _remote(_, __, event_dict):
            try:
        # Validate remote_url: must be HTTPS and optionally match a whitelist
        parsed_url = urlparse(remote_url)
        allowed_schemes = {"https"}
        if parsed_url.scheme not in allowed_schemes or not parsed_url.netloc:
            raise ValueError("remote_url must be a valid HTTPS URL")

        def _remote(_, __, event_dict):
            try:
                headers = {}
                if remote_auth_token:
                    headers["Authorization"] = f"Bearer {remote_auth_token}"
                requests.post(remote_url, json=event_dict, headers=headers, timeout=0.5)
            except Exception:
                pass
            return event_dict

        processors.append(_remote)

    processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )


def get_logger(name: str = __name__):
    """Return a configured structlog logger."""

    return structlog.get_logger(name)
