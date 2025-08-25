"""Tests for the tool registry enforcing RBAC and HITL."""
from pathlib import Path

import pytest

from jarvis.tools.registry import ToolsRegistry, ToolMeta
from jarvis.tools import environment_tools as et
from jarvis.tools.risk import ActionRequestApproval
from jarvis.auth.security_manager import SecurityManager


class DummyDB:
    def __init__(self, users):
        self._users = users

    def get_user(self, username):
        return self._users.get(username)

    def log_security_event(self, *args, **kwargs):
        return None


def test_high_risk_tool_rbac_and_hitl(monkeypatch, tmp_path):
    audit_file = Path("audit.log")
    if audit_file.exists():
        audit_file.write_text("")
    else:
        audit_file.touch()

    db = DummyDB({"alice": {"role": "admin"}, "bob": {"role": "user"}})
    sm = SecurityManager(db)
    sm.grant_role_command_access("admin", "echo")
    monkeypatch.setattr(et, "_confirm", lambda msg: True)

    registry = ToolsRegistry()
    registry.register_tool(
        "run_shell_command",
        ToolMeta(et.run_shell_command, ["shell"], risk_tier="high", required_role="admin"),
    )

    with pytest.raises(PermissionError):
        registry.run_tool("run_shell_command", "bob", sm, "echo hi")

    log = audit_file.read_text()
    assert "|bob|run_shell_command:denied" in log

    with pytest.raises(ActionRequestApproval):
        registry.run_tool(
            "run_shell_command", "alice", sm, "echo hi", approval_fn=lambda u, n: False
        )

    result = registry.run_tool(
        "run_shell_command", "alice", sm, "echo hi", approval_fn=lambda u, n: True
    )
    assert result.strip() == "hi"

    log = audit_file.read_text()
    assert "|alice|run_shell_command:executed" in log
