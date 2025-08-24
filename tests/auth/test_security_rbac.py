"""Tests for role-based access control in :mod:`jarvis.auth.security_manager`."""

from jarvis.auth.security_manager import SecurityManager


class DummyDB:
    """Simple in-memory user store for testing."""

    def __init__(self, users):
        self._users = users

    def get_user(self, username):
        return self._users.get(username)

    def log_security_event(self, *args, **kwargs):
        """No-op logger for compatibility with security manager."""
        return None


def test_role_based_command_permission() -> None:
    """Users inherit command permissions from their roles."""
    db = DummyDB({"alice": {"role": "dev"}, "bob": {"role": "viewer"}})
    sm = SecurityManager(db)
    sm.grant_role_command_access("dev", "echo")

    assert sm.has_command_access("alice", "echo hello")
    assert not sm.has_command_access("bob", "echo hello")


def test_role_based_path_permission(tmp_path) -> None:
    """Path access can be granted at the role level."""
    db = DummyDB({"alice": {"role": "dev"}})
    sm = SecurityManager(db)
    sm.grant_role_path_access("dev", str(tmp_path))

    assert sm.has_path_access("alice", str(tmp_path / "file.txt"))
