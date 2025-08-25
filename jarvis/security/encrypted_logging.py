from __future__ import annotations

"""Encrypted logging utilities leveraging :mod:`jarvis.security.vault`."""

import logging
from pathlib import Path
from typing import Union

from .vault import Vault


class EncryptedFileHandler(logging.Handler):
    """Logging handler that writes encrypted records to disk.

    Each log record is formatted, encrypted with the shared vault key, and
    appended to the target file as a newline-delimited token. The resulting
    file remains encrypted at rest until decrypted via the same vault key.
    """

    def __init__(self, path: Union[str, Path]):
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._vault = Vault()

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        token = self._vault.encrypt(msg.encode("utf-8"))
        with self.path.open("ab") as fh:
            fh.write(token + b"\n")
