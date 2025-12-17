"""Minimal ConstitutionalCritic implementation for compatibility.

This provides a very small class that mirrors the external interface used in
orchestration and allows tests to import the symbol without requiring the full
production implementation to be present in this phase of the rebranding.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConstitutionalCritic:
    """A lightweight placeholder critic used for testing.

    Attributes:
        name: Optional name for the critic (defaults to 'constitutional')
        mcp_client: optional mcp client instance (ignored by the shim)
    """
    name: str = "constitutional"
    mcp_client: Any | None = None

    def evaluate(self, content: str) -> dict:
        """Evaluate content and return a simple score dict."""
        return {"name": self.name, "score": 1.0, "notes": "placeholder"}
