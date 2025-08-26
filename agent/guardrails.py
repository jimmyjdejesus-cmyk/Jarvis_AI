"""HITL guardrails for potentially destructive actions."""
from __future__ import annotations

import os
import subprocess

def confirm_destructive_action(action: str) -> None:
    """Prompt the user to confirm a destructive action.

    Uses environment variable ``JARVIS_AUTOCONFIRM=1`` to auto-approve
    actions, which is useful for tests and automated environments.
    """
    if os.getenv("JARVIS_AUTOCONFIRM") == "1":
        return
    resp = input(f"Confirm {action}? (y/n): ").strip().lower()
    if resp not in {"y", "yes"}:
        raise PermissionError(f"Action not approved: {action}")

def guarded_commit(message: str) -> None:
    """Run ``git commit`` with a confirmation prompt."""
    confirm_destructive_action("git commit")
    subprocess.run(["git", "commit", "-m", message], check=True)
