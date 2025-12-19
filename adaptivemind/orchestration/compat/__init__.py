# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Compatibility layer for legacy orchestrator implementations.

This module provides backward compatibility for the legacy `apps.AdaptiveMind_Local.Orchestrator`
while delegating to the sophisticated `adaptivemind.orchestration.MultiAgentOrchestrator`.

This is part of the migration strategy to consolidate two parallel orchestrator systems
into a single, unified implementation.

Note:
    This compatibility layer is deprecated and will be removed in a future release.
    Please migrate to using `adaptivemind.orchestration.MultiAgentOrchestrator` directly.
"""

from __future__ import annotations

import warnings
from typing import Any

__all__ = ["LocalOrchestratorAdapter", "LocalAgentWrapper"]

# Import the sophisticated orchestrator
from ..orchestrator import MultiAgentOrchestrator
from ...agents.specialist_registry import get_specialist_registry

# Import compatibility classes
from .local_adapter import LocalOrchestratorAdapter, LocalAgentWrapper
