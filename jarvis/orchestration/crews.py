"""Predefined crew presets assembled from :class:`AgentSpec` definitions."""

from __future__ import annotations

from typing import List

try:  # Support direct module imports during tests
    from .orchestrator import AgentSpec
except Exception:  # pragma: no cover - fallback when package context missing
    from orchestrator import AgentSpec  # type: ignore


async def _audit_step(state: dict) -> dict:
    state["crew"] = "code_audit"
    return state


async def _research_step(state: dict) -> dict:
    state["crew"] = "research"
    return state


def CodeAuditCrew() -> List[AgentSpec]:
    """Preset crew for code auditing workflows."""
    return [AgentSpec(name="audit", fn=_audit_step, entry=True)]


def ResearchCrew() -> List[AgentSpec]:
    """Preset crew for research workflows."""
    return [AgentSpec(name="research", fn=_research_step, entry=True)]


__all__ = ["CodeAuditCrew", "ResearchCrew"]
