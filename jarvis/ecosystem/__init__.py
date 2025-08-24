"""Jarvis AI Ecosystem utilities.

This lightweight __init__ exposes only the minimal components required for
internal tests to avoid heavy optional dependencies."""

try:
    from .meta_intelligence import ExecutiveAgent, SpecialistAIAgent, AgentCapability, SystemHealth
except Exception:  # pragma: no cover
    ExecutiveAgent = None
    SpecialistAIAgent = None
    AgentCapability = None
    SystemHealth = None

__all__ = [
    "ExecutiveAgent",
    "SpecialistAIAgent",
    "AgentCapability",
    "SystemHealth",
]

"""Minimal ecosystem package for tests."""

from .meta_intelligence import ExecutiveAgent

__all__ = ["ExecutiveAgent"]

