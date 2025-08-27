"""Test configuration to ensure package imports and keyring isolation."""

import sys
from pathlib import Path

import pytest
import keyring
from keyring.backend import KeyringBackend
import importlib.util
import types

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub minimal ``jarvis.security.secret_manager`` to avoid heavy package imports
SEC_PATH = ROOT / "jarvis" / "security" / "secret_manager.py"
spec = importlib.util.spec_from_file_location("jarvis.security.secret_manager", SEC_PATH)
secret_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(secret_manager)
jarvis_pkg = types.ModuleType("jarvis")
security_pkg = types.ModuleType("jarvis.security")
security_pkg.secret_manager = secret_manager
jarvis_pkg.security = security_pkg
sys.modules.setdefault("jarvis", jarvis_pkg)
sys.modules.setdefault("jarvis.security", security_pkg)
sys.modules["jarvis.security.secret_manager"] = secret_manager


class _MemoryKeyring(KeyringBackend):
    """In-memory keyring backend for tests."""

    priority = 1

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, username: str) -> str | None:
        return self._store.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        self._store[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        self._store.pop((service, username), None)


@pytest.fixture(autouse=True)
def _isolate_keyring() -> None:
    """Use an in-memory keyring for each test to avoid side effects."""

    keyring.set_keyring(_MemoryKeyring())
    yield
