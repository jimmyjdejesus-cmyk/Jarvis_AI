"""Utilities for crash recovery of orchestrator state.

The recovery module provides simple helpers to persist the last known
workflow state to disk and to reload it when the system restarts.  This
allows the orchestrator to resume from the previous graph state after an
unexpected crash.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from agent.hitl.policy import HITLPolicy, ApprovalCallback

STATE_PATH = os.environ.get("JARVIS_RECOVERY_FILE", "last_state.json")


def load_state(path: str = STATE_PATH) -> Optional[Dict[str, Any]]:
    """Load the previously saved workflow state if it exists."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_state(
    state: Dict[str, Any],
    path: str = STATE_PATH,
    *,
    policy: HITLPolicy | None = None,
    modal: ApprovalCallback | None = None,
) -> None:
    """Persist the current workflow state to disk."""

    if policy and policy.requires_approval("file_write"):
        if modal is None:
            raise ValueError("Approval modal required for save_state")
        if not policy.request_approval_sync(
            "file_write", f"Save orchestrator state to {path}", modal
        ):
            return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def clear_state(
    path: str = STATE_PATH,
    *,
    policy: HITLPolicy | None = None,
    modal: ApprovalCallback | None = None,
) -> None:
    """Remove any persisted workflow state."""

    if os.path.exists(path):
        if policy and policy.requires_approval("file_delete"):
            if modal is None:
                raise ValueError("Approval modal required for clear_state")
            if not policy.request_approval_sync(
                "file_delete", f"Delete orchestrator state {path}", modal
            ):
                return
        os.remove(path)
