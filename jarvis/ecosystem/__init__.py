"""Jarvis AI ecosystem entry points."""

from .meta_intelligence import MetaAgent

# Backwards compatibility export used in older tests
ExecutiveAgent = MetaAgent

__all__ = ["MetaAgent", "ExecutiveAgent"]

