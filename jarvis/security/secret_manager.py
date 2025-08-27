"""Simple secrets manager backed by the OS keyring."""

from __future__ import annotations

from typing import Optional

import keyring
from keyring.errors import NoKeyringError

SERVICE_NAME = "jarvis"


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve ``name`` from the keyring.

    Parameters
    ----------
    name:
        Identifier of the secret to fetch.
    default:
        Value returned when the secret is unavailable or the keyring backend
        is missing.

    Returns
    -------
    Optional[str]
        The retrieved secret or ``default`` if not found.
    """
    try:
        value = keyring.get_password(SERVICE_NAME, name)
    except NoKeyringError:
        value = None
    return value if value is not None else default
