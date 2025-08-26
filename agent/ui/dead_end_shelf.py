"""Dead-end shelf component for negative path hints."""
from __future__ import annotations

from typing import Callable, List, Dict, Any
import logging

try:  # pragma: no cover - optional dependency
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None  # type: ignore

logger = logging.getLogger(__name__)


class DeadEndShelf:
    """Displays previously pruned paths and allows overrides."""

    def __init__(self, query_fn: Callable[[str, str], List[Dict[str, Any]]] ):
        """Create shelf with a function that returns negative path records."""

        self.query_fn = query_fn

    def render(self, project_id: str, task_fingerprint: str) -> None:  # pragma: no cover - UI
        """Render shelf inside Streamlit sidebar."""

        if st is None:
            raise RuntimeError("streamlit is not installed")

        dead_ends = self.query_fn(project_id, task_fingerprint)
        if not dead_ends:
            return

        st.sidebar.subheader("Dead-End Shelf")
        for idx, item in enumerate(dead_ends):
            label = item.get("reason", "unknown")
            if st.sidebar.button(label, key=f"dead_{idx}"):
                st.session_state["override"] = True
                logger.info("HITL.OverrideGranted", extra={"project_id": project_id})
                st.sidebar.success("Override granted")
