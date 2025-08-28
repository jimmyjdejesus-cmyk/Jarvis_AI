"""Test configuration to ensure package imports and keyring isolation."""

import pytest
import keyring
from keyring.backend import KeyringBackend
import importlib.util
import types
from pathlib import Path
import sys
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import asyncio
import json
import logging
import os
import uuid
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, Callable, Awaitable

from jarvis.agents.agent_resources import (
    AgentCapability,
    AgentMetrics,
    SystemEvolutionPlan,
    SystemHealth,
)
from jarvis.agents.base import AIAgent
from jarvis.agents.critics import (
    BlueTeamCritic,
    ConstitutionalCritic,
    CriticFeedback,
    CriticVerdict,
    RedTeamCritic,
    WhiteGate,
)
from jarvis.agents.curiosity_agent import CuriosityAgent
from jarvis.agents.curiosity_router import CuriosityRouter
from jarvis.agents.mission_planner import MissionPlanner
from jarvis.agents.specialist import SpecialistAgent
from jarvis.memory.project_memory import MemoryManager, ProjectMemory
from jarvis.monitoring.performance import CriticInsightMerger, PerformanceTracker
from jarvis.homeostasis import SystemMonitor
from jarvis.orchestration.orchestrator import (
    AgentSpec,
    DynamicOrchestrator,
    MultiAgentOrchestrator,
)
from jarvis.orchestration.sub_orchestrator import SubOrchestrator
from jarvis.persistence.session import SessionManager
from jarvis.world_model.knowledge_graph import KnowledgeGraph
from jarvis.world_model.hypergraph import HierarchicalHypergraph
from jarvis.workflows.engine import (
    WorkflowEngine,
    WorkflowStatus,
    add_custom_task,
    create_workflow,
)

@pytest.fixture
def mock_neo4j_graph(monkeypatch):
    """Provide a mock Neo4j graph for tests.

    This fixture patches both the Neo4jGraph class used by core modules and the
    instantiated ``neo4j_graph`` in ``app.main`` so tests can run without a
    real database connection.
    """

    mock_graph = MagicMock()
    # Mock methods that are called during tests
    mock_graph.connect = MagicMock()
    mock_graph.close = MagicMock()
    mock_graph.run = MagicMock(return_value=MagicMock(data=MagicMock(return_value=[])))

    monkeypatch.setattr(
        "jarvis.world_model.neo4j_graph.Neo4jGraph", MagicMock(return_value=mock_graph)
    )
    yield mock_graph

class ExecutiveAgent(AIAgent):