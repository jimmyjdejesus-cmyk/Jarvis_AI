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
import queue
import threading


def configure(
    log_file: str = "logs/jarvis.log",
    remote_url: Optional[str] = None,
    remote_auth_token: Optional[str] = None,
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
    force=True,
    )

    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if remote_url:
        # Validate remote_url: must be HTTPS and optionally match a whitelist
        from urllib.parse import urlparse
        parsed_url = urlparse(remote_url)
        allowed_schemes = {"https"}
        if parsed_url.scheme not in allowed_schemes or not parsed_url.netloc:
            raise ValueError("remote_url must be a valid HTTPS URL")

        # Set up a background queue and worker thread for async remote logging
        remote_log_queue = queue.Queue()

        def _remote_worker():
            while True:
                item = remote_log_queue.get()
                if item is None:
                    break  # Sentinel for shutdown
                try:
                    requests.post(remote_url, json=item, timeout=0.5)
                except Exception:
                    pass
                finally:
                    remote_log_queue.task_done()

        remote_thread = threading.Thread(target=_remote_worker, daemon=True)
        remote_thread.start()

        def _remote(_, __, event_dict):
            try:
                headers = {}
                if remote_auth_token is not None:
                    headers["Authorization"] = f"Bearer {remote_auth_token}"
                remote_log_queue.put_nowait(event_dict.copy())
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


def get_logger(name: str = None):
    """Return a configured structlog logger."""
    if name is None:
        import inspect
        frame = inspect.currentframe()
        caller_frame = frame.f_back if frame else None
        name = caller_frame.f_globals["__name__"] if caller_frame and "__name__" in caller_frame.f_globals else __name__
    return structlog.get_logger(name)
