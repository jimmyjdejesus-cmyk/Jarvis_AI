"""Lightweight agents package used in tests.

Only a small subset of the full project agents are exposed here with guarded
imports to avoid heavy optional dependencies during testing.
"""

from __future__ import annotations

# Core planning and curiosity utilities
try:  # pragma: no cover - optional dependencies
    from .mission_planner import MissionPlanner
except Exception:  # pragma: no cover
    MissionPlanner = None  # type: ignore

try:  # pragma: no cover - optional dependencies
    from .curiosity_agent import CuriosityAgent
except Exception:  # pragma: no cover
    CuriosityAgent = None  # type: ignore

# Optional specialist agents – failure to import simply leaves them as ``None``
try:  # pragma: no cover
    from .coding_agent import CodingAgent, get_coding_agent
except Exception:  # pragma: no cover
    CodingAgent = None  # type: ignore

    def get_coding_agent(*_args, **_kwargs):  # type: ignore
        raise ImportError("CodingAgent not available")

from .base_specialist import BaseSpecialist
from .simulation_agent import SimulationAgent
from .monte_carlo_explorer import MonteCarloExplorer
from .benchmark_agent import BenchmarkRewardAgent
from .decentralized_actor import DecentralizedActor

try:
    from .live_test_agent import LiveTestAgent
except Exception:  # pragma: no cover
    LiveTestAgent = None

# New specialist agents
try:
    from .specialist import SpecialistAgent
    from .specialists import (
        CodeReviewAgent,
        SecurityAgent,
        ArchitectureAgent,
        TestingAgent,
        DevOpsAgent
    )
    from .critics import RedTeamCritic
    
    # Add specialist agents to exports
    __all__ = [
        'CodingAgent',
        'get_coding_agent',
        'MissionPlanner',
        'BaseSpecialist',
        'SimulationAgent',
        'MonteCarloExplorer',
        'CuriosityAgent',
        'BenchmarkRewardAgent',
        'LiveTestAgent',
        'SpecialistAgent',
        'CodeReviewAgent',
        'SecurityAgent',
        'ArchitectureAgent',
        'TestingAgent',
        'DevOpsAgent',
        'RedTeamCritic',
        'DecentralizedActor'
    ]
    
except Exception:  # pragma: no cover
    # Fallback if specialist agents not available
    __all__ = [
        'CodingAgent',
        'get_coding_agent',
        'MissionPlanner',
        'SimulationAgent',
        'MonteCarloExplorer',
        'CuriosityAgent',
        'BenchmarkRewardAgent',
        'LiveTestAgent',
        'DecentralizedActor'
    ]