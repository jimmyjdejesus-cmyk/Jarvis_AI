"""Streamlit sidebar components for the Jarvis desktop application.

The original project left this module empty.  For the purposes of the tests and
examples in this repository we provide a very small control panel that allows a
user to select the language model and toggle a couple of runtime options.  The
values are stored in ``st.session_state`` so that other pages can access them.
"""

from __future__ import annotations

import streamlit as st

try:  # pragma: no cover - helper may not be available in minimal environment
    from scripts import get_available_models
except Exception:  # fallback for test environment
    def get_available_models():  # type: ignore
        return ["llama3.2", "qwen2.5", "gemma2"]


def sidebar() -> None:
    """Render the sidebar control panel."""

    st.sidebar.header("Controls")

    models = get_available_models()
    st.session_state.setdefault("selected_model", models[0])
    model = st.sidebar.selectbox("Model", models, index=models.index(st.session_state["selected_model"]))
    st.session_state["selected_model"] = model

    st.session_state["stream_enabled"] = st.sidebar.checkbox("Stream responses", value=True)
    st.session_state["hitl_required"] = st.sidebar.checkbox(
        "Require HITL for destructive actions", value=True
    )


__all__ = ["sidebar"]
