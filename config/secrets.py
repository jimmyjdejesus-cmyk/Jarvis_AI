"""Secrets management using python-dotenv and OS keychain."""

from __future__ import annotations

import logging
import os
from typing import Iterable, Optional

import keyring
from dotenv import load_dotenv

load_dotenv()

SERVICE_NAME = "jarvis-ai"


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve a secret from the OS keychain or environment variables."""
    try:
        value = keyring.get_password(SERVICE_NAME, key)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(key, default)


def set_secret(key: str, value: str) -> None:
    """Store a secret in the OS keychain."""
    try:
        keyring.set_password(SERVICE_NAME, key, value)
    except Exception:
        pass


class SecretFilter(logging.Filter):
    """Logging filter that masks known secrets."""

    def __init__(self, secrets: Iterable[str]):
        self.secrets = [s for s in secrets if s]

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        message = record.getMessage()
        for secret in self.secrets:
            message = message.replace(secret, "***")
        record.msg = message
        return True


def apply_secret_filter(logger: logging.Logger, keys: Iterable[str]) -> None:
    """Apply secret masking filter to a logger for specified keys."""
    secrets = [get_secret(key) for key in keys]
    logger.addFilter(SecretFilter(secrets))
