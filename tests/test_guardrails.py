import builtins
import os
import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from agent.guardrails import confirm_destructive_action


def test_confirm_destructive_action_approve(monkeypatch):
    monkeypatch.setenv("JARVIS_AUTOCONFIRM", "0")
    monkeypatch.setattr(builtins, "input", lambda _: "y")
    confirm_destructive_action("write file")  # should not raise


def test_confirm_destructive_action_deny(monkeypatch):
    monkeypatch.setenv("JARVIS_AUTOCONFIRM", "0")
    monkeypatch.setattr(builtins, "input", lambda _: "n")
    with pytest.raises(PermissionError):
        confirm_destructive_action("write file")


def test_auto_confirm(monkeypatch):
    calls = []

    def fake_input(prompt):
        calls.append(prompt)
        return "n"

    monkeypatch.setenv("JARVIS_AUTOCONFIRM", "1")
    monkeypatch.setattr(builtins, "input", fake_input)
    confirm_destructive_action("write file")
    assert not calls
