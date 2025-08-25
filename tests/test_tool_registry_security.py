"""Tests for tool registry RBAC and HITL security."""

import logging
import pytest
import asyncio
import importlib.util
import pathlib
from typing import Any

from agent.hitl.policy import HITLPolicy
from jarvis.auth.security_manager import SecurityManager
from jarvis.tools.registry import Registry
from jarvis.tools import environment_tools

_main_spec = importlib.util.spec_from_file_location(
    "jarvis_app_main", pathlib.Path(__file__).resolve().parents[1] / "app" / "main.py"
)
_main = importlib.util.module_from_spec(_main_spec)
_main_spec.loader.exec_module(_main)
app = _main.app
hitl_gates = _main.hitl_gates
approve = _main.approve
deny = _main.deny


class DummyDB:
    """In-memory user store for role lookup."""

    def __init__(self, users):
        self._users = users

    def get_user(self, username):
        return self._users.get(username)

    def log_security_event(self, *args, **kwargs):
        return None


def allow(_):
    return True


def test_high_risk_tool_requires_role_and_hitl(caplog):
    db = DummyDB({"alice": {"role": "admin"}, "bob": {"role": "user"}})
    sm = SecurityManager(db)
    policy = HITLPolicy()
    registry = Registry()

    def dangerous(x: int) -> int:
        return x * 2

    registry.register(
        "danger",
        dangerous,
        "Multiply numbers dangerously",
        ["test"],
        risk_tier="high",
        required_role="admin",
    )

    with caplog.at_level(logging.WARNING):
        with pytest.raises(PermissionError):
            registry.execute(
                "danger", 1, user="bob", security=sm, hitl=policy, modal=allow
            )
        assert any("RBACDenied" in rec.message for rec in caplog.records)

    with caplog.at_level(logging.INFO):
        assert (
            registry.execute(
                "danger", 2, user="alice", security=sm, hitl=policy, modal=allow
            )
            == 4
        )
        assert policy.audit[-1].user == "alice"
        assert any("ToolExecuted" in rec.message for rec in caplog.records)


def test_hitl_endpoints_update_gate():
    asyncio.run(approve(_main.HitlDecision(action="t1")))
    assert hitl_gates["t1"] is True
    asyncio.run(deny(_main.HitlDecision(action="t2")))
    assert hitl_gates["t2"] is False


def modal_deny(_):
    return False


def test_shell_command_denied_by_hitl(caplog):
    db = DummyDB({"alice": {"role": "admin"}})
    sm = SecurityManager(db)
    sm.grant_command_access("alice", "echo")
    policy = HITLPolicy()
    registry = Registry()

    def shell(command: str, username: str, security_manager: Any = None) -> None:
        environment_tools.run_shell_command(command, username, security_manager)

    registry.register(
        "shell",
        shell,
        "Run shell command",
        ["shell"],
        risk_tier="high",
        required_role="admin",
    )

    with caplog.at_level(logging.WARNING):
        with pytest.raises(PermissionError):
            registry.execute(
                "shell",
                "echo hi",
                "alice",
                user="alice",
                security=sm,
                hitl=policy,
                modal=modal_deny,
                security_manager=sm,
            )
        assert any("HITLDenied" in rec.message for rec in caplog.records)


def test_write_file_denied_by_hitl(tmp_path, caplog):
    db = DummyDB({"alice": {"role": "admin"}})
    sm = SecurityManager(db)
    sm.grant_path_access("alice", str(tmp_path))
    policy = HITLPolicy()
    registry = Registry()

    def writer(path: str, content: str, username: str, security_manager: Any = None) -> bool:
        return environment_tools.write_file(path, content, username, security_manager)

    registry.register(
        "write",
        writer,
        "Write file",
        ["fs"],
        risk_tier="high",
        required_role="admin",
    )

    target = tmp_path / "out.txt"
    with caplog.at_level(logging.WARNING):
        with pytest.raises(PermissionError):
            registry.execute(
                "write",
                str(target),
                "data",
                "alice",
                user="alice",
                security=sm,
                hitl=policy,
                modal=modal_deny,
                security_manager=sm,
            )
        assert any("HITLDenied" in rec.message for rec in caplog.records)
    assert not target.exists()