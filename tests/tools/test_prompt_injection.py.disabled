from __future__ import annotations

from jarvis.auth.security_manager import SecurityManager
from jarvis.tools.environment_tools import run_shell_command


def test_run_shell_command_sanitizes(monkeypatch) -> None:
    sm = SecurityManager()
    sm.grant_command_access("alice", "echo")
    monkeypatch.setattr("jarvis.tools.environment_tools._confirm", lambda msg: True)
    out = run_shell_command("echo hello; rm -rf /", "alice", sm)
    assert out.strip() == "hello rm -rf /"
