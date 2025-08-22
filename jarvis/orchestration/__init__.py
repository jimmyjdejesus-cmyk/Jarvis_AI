# Orchestration Package
"""
Multi-agent orchestration system for coordinating specialist AI agents

This package provides:
- MultiAgentOrchestrator: Coordinates multiple specialists for complex tasks
- SubOrchestrator: Scoped orchestrator used for nested missions
- Workflow management and task delegation
- Result synthesis and conflict resolution
This package provides building blocks for creating LangGraph based
orchestration workflows.  The previous specialised orchestrator has been
replaced by a small, generic template which can dynamically assemble graphs
from ``AgentSpec`` definitions.
"""

from .orchestrator import MultiAgentOrchestrator, AgentSpec, DynamicOrchestrator, END
from .sub_orchestrator import SubOrchestrator

from .pruning import PruningManager
from .orchestrator import AgentSpec, DynamicOrchestrator, END



__all__ = [
    "AgentSpec",
    "DynamicOrchestrator",
    "MultiAgentOrchestrator",
    "SubOrchestrator",

    "PruningManager",
    "END",

# Version info
__version__ = "1.0.0"
__author__ = "Jarvis AI Team"
