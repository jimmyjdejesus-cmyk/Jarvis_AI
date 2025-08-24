"""
Jarvis AI Agents - Specialized AI assistants and expert agents
"""

# Legacy coding agent
try:
    from .coding_agent import CodingAgent, get_coding_agent
except Exception:  # pragma: no cover
    CodingAgent = None

    def get_coding_agent(*args, **kwargs):  # type: ignore
        raise ImportError("CodingAgent not available")
from .mission_planner import MissionPlanner
from .base_specialist import BaseSpecialist
from .simulation_agent import SimulationAgent
from .monte_carlo_explorer import MonteCarloExplorer
from .curiosity_agent import CuriosityAgent
from .benchmark_agent import BenchmarkRewardAgent
from .live_test_agent import LiveTestAgent

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
        'RedTeamCritic'
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
        'LiveTestAgent'
    ]

# Version info
__version__ = "2.0.0"
__author__ = "Jarvis AI Team"

