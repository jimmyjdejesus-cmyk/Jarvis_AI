"""
Jarvis AI Agents - Specialized AI assistants and expert agents
"""

# Legacy coding agent
from .coding_agent import CodingAgent, get_coding_agent

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
        'SpecialistAgent',
        'CodeReviewAgent',
        'SecurityAgent',
        'ArchitectureAgent', 
        'TestingAgent',
        'DevOpsAgent',
        'RedTeamCritic'
    ]
    
except ImportError:
    # Fallback if specialist agents not available
    __all__ = ['CodingAgent', 'get_coding_agent']

# Version info
__version__ = "2.0.0"
__author__ = "Jarvis AI Team"
