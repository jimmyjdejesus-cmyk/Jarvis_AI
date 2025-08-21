"""
Jarvis AI Agents - Specialized AI assistants and expert agents
"""

# Legacy coding agent
from .coding_agent import CodingAgent, get_coding_agent
from .mission_planner import MissionPlanner

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
    
    # Add specialist agents to exports
    __all__ = [
        'CodingAgent',
        'get_coding_agent',
        'MissionPlanner',
        'SpecialistAgent',
        'CodeReviewAgent',
        'SecurityAgent',
        'ArchitectureAgent',
        'TestingAgent',
        'DevOpsAgent'
    ]
    
except ImportError:
    # Fallback if specialist agents not available
    __all__ = ['CodingAgent', 'get_coding_agent', 'MissionPlanner']

# Version info
__version__ = "2.0.0"
__author__ = "Jarvis AI Team"
