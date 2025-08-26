"""Jarvis AI ecosystem entry points."""

from .meta_intelligence import ExecutiveAgent

# Backwards compatibility export used in older tests
MetaAgent = ExecutiveAgent

__all__ = ["MetaAgent", "ExecutiveAgent"]

