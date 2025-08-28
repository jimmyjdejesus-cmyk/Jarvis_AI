from __future__ import annotations

# flake8: noqa
from pathlib import Path
from unittest.mock import MagicMock
import sys
import types
import importlib.util
import enum
from dataclasses import dataclass
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub optional dependencies
sys.modules.setdefault("neo4j", MagicMock())
keyring_errors = types.ModuleType("keyring.errors")


class NoKeyringError(Exception):
    pass


keyring_errors.NoKeyringError = NoKeyringError
keyring_module = types.ModuleType("keyring")
keyring_module.errors = keyring_errors
keyring_module.get_password = lambda *args, **kwargs: None
sys.modules.setdefault("keyring", keyring_module)
sys.modules.setdefault("keyring.errors", keyring_errors)

langgraph_graph = types.ModuleType("langgraph.graph")
langgraph_graph.END = object()


class StateGraph:  # pragma: no cover - minimal stub
    pass


langgraph_graph.StateGraph = StateGraph
langgraph_module = types.ModuleType("langgraph")
langgraph_module.graph = langgraph_graph
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", langgraph_graph)
# Minimal qdrant_client stub so imports succeed without the heavy dependency
qdrant_client = types.ModuleType("qdrant_client")
qdrant_client.QdrantClient = MagicMock()
qdrant_models = types.ModuleType("qdrant_client.models")
qdrant_client.models = qdrant_models
sys.modules.setdefault("qdrant_client", qdrant_client)
sys.modules.setdefault("qdrant_client.models", qdrant_models)
for name in [
    "Distance",
    "FieldCondition",
    "Filter",
    "MatchValue",
    "PointStruct",
    "VectorParams",
]:
    setattr(qdrant_models, name, MagicMock())