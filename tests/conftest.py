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

# Provide lightweight stand-ins for optional external dependencies
jarvis_pkg = types.ModuleType("jarvis")
critics_pkg = types.ModuleType("jarvis.agents.critics")
critics_pkg.__path__ = [str(JARVIS_PATH / "agents" / "critics")]
constitutional_critic = types.ModuleType("jarvis.agents.critics.constitutional_critic")
class ConstitutionalCritic:  # pragma: no cover - stub
    def __init__(self, *args, **kwargs):
        pass
constitutional_critic.ConstitutionalCritic = ConstitutionalCritic
sys.modules.setdefault("jarvis.agents.critics", critics_pkg)
sys.modules.setdefault("jarvis.agents.critics.constitutional_critic", constitutional_critic)

orch_pkg = types.ModuleType("jarvis.orchestration")
orch_pkg.__path__ = [str(JARVIS_PATH / "orchestration")]
sys.modules.setdefault("jarvis.orchestration", orch_pkg)

jarvis_pkg.__path__ = [str(JARVIS_PATH)]
sys.modules.setdefault("jarvis", jarvis_pkg)

# Provide lightweight stand-ins for optional external dependencies
chromadb = types.ModuleType('chromadb')
chromadb.utils = types.ModuleType('utils')
memory_service = types.ModuleType("memory_service")
class PathRecord:
    pass
class PathSignature:
    pass
class Outcome:
    pass
class Metrics:
    pass
class NegativeCheck:
    pass
def record_path(*args, **kwargs):
    return None
def avoid_negative(*args, **kwargs):
    return False
memory_service.record_path = record_path
memory_service.avoid_negative = avoid_negative
memory_service.PathRecord = PathRecord
memory_service.PathSignature = PathSignature
memory_service.Outcome = Outcome
memory_service.Metrics = Metrics
memory_service.NegativeCheck = NegativeCheck
class _VectorStore:
    def add_text(self, *args, **kwargs):
        return None
    def query_text(self, query, n_results=1):
        return {"documents": [[]]}
memory_service.vector_store = _VectorStore()

sys.modules.setdefault("memory_service", memory_service)

pydantic = types.ModuleType("pydantic")
class BaseModel:  # pragma: no cover - stub
    pass
def Field(default=None, *args, **kwargs):  # pragma: no cover - stub
    return default
pydantic.BaseModel = BaseModel
pydantic.Field = Field
sys.modules.setdefault("pydantic", pydantic)

langgraph = types.ModuleType("langgraph")
langgraph.graph = types.ModuleType("graph")
langgraph.graph.END = object()
class StateGraph:  # pragma: no cover - stub
    pass
langgraph.graph.StateGraph = StateGraph
sys.modules.setdefault("langgraph", langgraph)
sys.modules.setdefault("langgraph.graph", langgraph.graph)

chromadb.utils.embedding_functions = types.ModuleType('embedding_functions')

class EmbeddingFunction:  # pragma: no cover - simple stub
    """Minimal base embedding function stub."""

class HashEmbeddingFunction(EmbeddingFunction):  # pragma: no cover - simple stub
    """Hash-based embedding function stub."""

chromadb.utils.embedding_functions.EmbeddingFunction = EmbeddingFunction
chromadb.utils.embedding_functions.HashEmbeddingFunction = HashEmbeddingFunction
sys.modules.setdefault('chromadb', chromadb)
sys.modules.setdefault('chromadb.utils', chromadb.utils)
sys.modules.setdefault('chromadb.utils.embedding_functions', chromadb.utils.embedding_functions)

neo4j_module = types.ModuleType('neo4j')

class GraphDatabase:  # pragma: no cover - simple stub
    """Stub GraphDatabase with no-op driver."""

    @staticmethod
    def driver(*args, **kwargs):
        return None

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