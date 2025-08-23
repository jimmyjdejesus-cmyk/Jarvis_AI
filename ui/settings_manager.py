"""Settings UI for managing API keys and tokens."""

from __future__ import annotations

import os
from typing import Dict

import streamlit as st

from v2.config.config import save_secrets


class SettingsManager:
    """Provide a Streamlit interface for editing secrets."""

    def render_settings_ui(self) -> None:
        """Render the settings page with secret inputs and save support."""
        st.title("⚙️ Settings")
        secrets: Dict[str, str] = {}

        # LLM provider keys
        with st.expander("LLM Providers"):
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
            )
            anthropic_key = st.text_input(
                "Anthropic API Key",
                type="password",
                value=os.getenv("ANTHROPIC_API_KEY", ""),
            )
            if openai_key:
                secrets["OPENAI_API_KEY"] = openai_key
            if anthropic_key:
                secrets["ANTHROPIC_API_KEY"] = anthropic_key

        # Observability tools
        with st.expander("Observability Tools"):
            langsmith_key = st.text_input(
                "LangSmith API Key",
                type="password",
                value=os.getenv("LANGSMITH_API_KEY", ""),
            )
            if langsmith_key:
                secrets["LANGSMITH_API_KEY"] = langsmith_key

        # Version control tokens
        with st.expander("Version Control"):
            github_token = st.text_input(
                "GitHub Token",
                type="password",
                value=os.getenv("GITHUB_TOKEN", ""),
            )
            if github_token:
                secrets["GITHUB_TOKEN"] = github_token

        if st.button("Save Settings"):
            save_secrets(secrets)
            st.success("Settings saved successfully.")


__all__ = ["SettingsManager"]
