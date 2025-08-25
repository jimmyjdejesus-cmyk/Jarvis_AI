from __future__ import annotations

"""Lightweight secrets vault using symmetric encryption.

The vault centralizes retrieval of the encryption key used to protect
sensitive data at rest. The key is loaded from the ``JARVIS_VAULT_KEY``
environment variable or from a path specified by ``JARVIS_VAULT_KEY_FILE``.
If neither is provided, a transient key is generated for the process."""

import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet


class Vault:
    """Simple wrapper around ``Fernet`` for encrypting data at rest."""

    def __init__(self, key: Optional[bytes] = None) -> None:
        if key is None:
            env_key = os.getenv("JARVIS_VAULT_KEY")
            if env_key:
                key = env_key.encode()
            else:
                key_file = os.getenv("JARVIS_VAULT_KEY_FILE")
                if key_file and Path(key_file).exists():
                    key = Path(key_file).read_bytes().strip()
        if key is None:
            key = Fernet.generate_key()
        self.key = key
        self._fernet = Fernet(self.key)

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt ``data`` returning a token suitable for storage."""

        return self._fernet.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        """Decrypt ``token`` produced by :meth:`encrypt`."""

        return self._fernet.decrypt(token)
