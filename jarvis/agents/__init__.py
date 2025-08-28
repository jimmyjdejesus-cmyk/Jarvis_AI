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

# Optional curiosity question routing
try:  # pragma: no cover - optional dependencies
    from .curiosity_router import CuriosityRouter
except Exception:  # pragma: no cover
    CuriosityRouter = None  # type: ignore

# Optional specialist agents – defer import to avoid heavy dependencies
CodingAgent = None  # type: ignore


def get_coding_agent(*_args, **_kwargs):  # type: ignore
    raise ImportError("CodingAgent not available")

from .base_specialist import BaseSpecialist
try:  # pragma: no cover - optional dependencies
    from .simulation_agent import SimulationAgent
except Exception:  # pragma: no cover
    SimulationAgent = None  # type: ignore

try:  # pragma: no cover - optional dependencies
    from .monte_carlo_explorer import MonteCarloExplorer
except Exception:  # pragma: no cover
    MonteCarloExplorer = None  # type: ignore

try:  # pragma: no cover - optional dependencies
    from .benchmark_agent import BenchmarkRewardAgent
except Exception:  # pragma: no cover
    BenchmarkRewardAgent = None  # type: ignore

try:  # pragma: no cover - optional dependencies
    from .decentralized_actor import DecentralizedActor
except Exception:  # pragma: no cover
    DecentralizedActor = None  # type: ignore

try:
    from .live_test_agent import LiveTestAgent
except Exception:  # pragma: no cover
    LiveTestAgent = None

# New specialist agents
try:
    from .specialist import SpecialistAgent
    from .specialists import (
        CodeReviewAgent,
        ArchitectureAgent,
        TestingAgent,
        DevOpsAgent,
        CloudCostOptimizerAgent,
        UserFeedbackAgent,
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
        'CuriosityRouter',
        'BenchmarkRewardAgent',
        'LiveTestAgent',
        'SpecialistAgent',
        'CodeReviewAgent',
        'ArchitectureAgent',
        'TestingAgent',
        'DevOpsAgent',
        'CloudCostOptimizerAgent',
        'UserFeedbackAgent',
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
        'CuriosityRouter',
        'BenchmarkRewardAgent',
        'LiveTestAgent',
        'DecentralizedActor',
    ]
