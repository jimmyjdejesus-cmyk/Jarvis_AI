"""Tests for RBAC enforcement in :mod:`jarvis.tools.environment_tools`."""

import pytest

from jarvis.auth.security_manager import SecurityManager
from jarvis.tools import environment_tools as et


class DummyDB:
    """Simple in-memory user store for testing."""

    def __init__(self, users):
        self._users = users

    def get_user(self, username):
        return self._users.get(username)

    def log_security_event(self, *args, **kwargs):
        """Placeholder for database logging used in tests."""
        return None


def test_environment_tools_respect_rbac(monkeypatch, tmp_path) -> None:
    """Role permissions enable full read/write/exec access."""
    db = DummyDB({"alice": {"role": "dev"}})
    sm = SecurityManager(db)
    sm.grant_role_path_access("dev", str(tmp_path))
    sm.grant_role_command_access("dev", "echo")
    monkeypatch.setattr(et, "_confirm", lambda msg: True)

    file_path = tmp_path / "data.txt"
    assert et.write_file(str(file_path), "hi", "alice", sm)
    assert et.read_file(str(file_path), "alice", sm) == "hi"
    assert et.run_shell_command("echo hi", "alice", sm).strip() == "hi"


def test_run_shell_command_denied_without_permission(monkeypatch) -> None:
    """Users without command rights are blocked."""
    db = DummyDB({"bob": {"role": "viewer"}})
    sm = SecurityManager(db)
    monkeypatch.setattr(et, "_confirm", lambda msg: True)

    with pytest.raises(PermissionError):
        et.run_shell_command("echo hi", "bob", sm)


def test_write_requires_confirmation(monkeypatch, tmp_path) -> None:
    """High-impact operations require explicit confirmation."""
    db = DummyDB({"alice": {"role": "dev"}})
    sm = SecurityManager(db)
    sm.grant_role_path_access("dev", str(tmp_path))
    monkeypatch.setattr(et, "_confirm", lambda msg: False)

    assert not et.write_file(str(tmp_path / "a.txt"), "x", "alice", sm)


def test_read_permission_denied(monkeypatch, tmp_path) -> None:
    """Reading without path permission raises an error."""
    db = DummyDB({"bob": {"role": "viewer"}})
    sm = SecurityManager(db)
    monkeypatch.setattr(et, "_confirm", lambda msg: True)

    with pytest.raises(PermissionError):
        et.read_file(str(tmp_path / "a.txt"), "bob", sm)
