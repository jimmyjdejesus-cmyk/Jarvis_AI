"""Test configuration to ensure package imports and keyring isolation."""

import pytest
import keyring
from keyring.backend import KeyringBackend
import importlib.util
import types
from pathlib import Path
import sys
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def mock_neo4j_graph(monkeypatch):
    """Provide a mock Neo4j graph for tests.

    This fixture patches both the Neo4jGraph class used by core modules and the
    instantiated ``neo4j_graph`` in ``app.main`` so tests can run without a
    real database connection.
    """

    mock_graph = MagicMock()

    try:
        import jarvis.world_model.neo4j_graph as neo_module
        monkeypatch.setattr(neo_module, "Neo4jGraph", MagicMock(return_value=mock_graph))
    except Exception:
        pass

    try:
        import app.main as main_app
        monkeypatch.setattr(main_app, "neo4j_graph", mock_graph)
    except Exception:
        pass

    return mock_graph

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