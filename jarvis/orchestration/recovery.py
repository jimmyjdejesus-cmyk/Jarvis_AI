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

STATE_PATH = os.environ.get("JARVIS_RECOVERY_FILE", "last_state.json")


def load_state(path: str = STATE_PATH) -> Optional[Dict[str, Any]]:
    """Load the previously saved workflow state if it exists."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_state(state: Dict[str, Any], path: str = STATE_PATH) -> None:
    """Persist the current workflow state to disk."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def clear_state(path: str = STATE_PATH) -> None:
    """Remove any persisted workflow state."""
    if os.path.exists(path):
        os.remove(path)
