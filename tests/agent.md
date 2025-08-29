"""Test cases for the main FastAPI application."""
from __future__ import annotations

from typing import Any, Dict
import pytest
from fastapi.testclient import TestClient
from app.main import app, create_test_app
from jarvis.memory.memory_bus import MemoryBus
from jarvis.memory.replay_memory import ReplayMemory

# In-memory store for missions
mission_history: Dict[str, Any] = {}


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_read_main(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Jarvis AI"}

# Attempt to import the full Jarvis orchestration system
# If it fails, create mock objects to allow the server to run for frontend development
try:
    from jarvis.agents.base_specialist import BaseSpecialist
    from jarvis.agents.curiosity_agent import CuriosityAgent
    from jarvis.agents.mission_planner import MissionPlanner
    from jarvis.core.mcp_agent import MCPJarvisAgent
    from jarvis.orchestration.mission import Mission, MissionDAG
    from jarvis.orchestration.orchestrator import MultiAgentOrchestrator
    from jarvis.world_model.hypergraph import HierarchicalHypergraph
    from jarvis.world_model.neo4j_graph import Neo4jGraph
    from jarvis.workflows.engine import WorkflowStatus, from_mission_dag, workflow_engine
    JARVIS_AVAILABLE = True
    logger.info("✅ Jarvis orchestration system loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Jarvis orchestration not available, using mock objects: {e}")
    
    JARVIS_AVAILABLE = False
# Agent Log - tests
- Added unit tests for `CuriosityRouter` covering enqueue behavior and disabled mode.
# Agent Log
- Added tests for `run_step` timeout handling, retry backoff, and performance tracking.
## Agent Log 2025-08-31
- Updated CLI tests to use ExecutiveAgent.
- Added multi-step mission test verifying mission results and execution graph output.
## Agent Log 2025-09-01
- Added docstrings and failure scenario tests for CLI.
- Ensured tests meet PEP 8 using flake8.
## Agent Log 2025-09-02
- Verified CLI returns mission result through updated unit test.
## Agent Log 2025-09-03
- Added integration test exercising MCPClient against an aiohttp server.
## Agent Log 2025-09-04
- Expanded MCPClient integration tests to include server error handling and tool execution.
## Agent Log 2025-09-05
- Added integration tests covering authentication failures and request timeouts for MCPClient.
## Agent Interaction
**Timestamp:** 2025-08-28T23:07:00+00:00
**Agent ID:** openai-assistant
**Team:** tests
**Action/Message:**
```
Adjusted test_cli to patch ExecutiveAgent and handle new run subcommand.
```
**Associated Data:**
```
File: test_cli.py
```
---

## Agent Interaction
**Timestamp:** 2025-08-28T23:07:00+00:00
=======

def test_get_mission_history():
    """Test mission history retrieval via the API."""
    test_app = create_test_app(mission_history)
    client = TestClient(test_app)

## Agent Interaction
**Timestamp:** 2025-08-28T02:28:19+00:00
**Agent ID:** openai-assistant
**Team:** tests
**Action/Message:**
```
Wrapped long lines in test_knowledge_query_get to satisfy flake8 E501.
File is quite long; consider archiving older entries soon.
```
**Associated Data:**
```
File: tests/test_knowledge_query_get.py
```
---
## Agent Log
- 2024-05-29: Added workflow execution test for ExecutiveAgent.
- Added tests for specialist dispatch timeout and retry behavior.
- Consolidated dependency stubs in `conftest.py` and added successful retry test for dispatch logic.
- Refactored `test_orchestrator_auction` to run without async plugin.
## Agent Log 2025-08-31
- Updated CLI tests to use ExecutiveAgent.
- Added multi-step mission test verifying mission results and execution graph output.
## Agent Log 2025-09-01
- Added docstrings and failure scenario tests for CLI.
- Ensured tests meet PEP 8 using flake8.
## Agent Log 2025-09-02
- Verified CLI returns mission result through updated unit test.
## Dev Log
- Added tests for curiosity routing to ensure directives execute when enabled and skip when disabled.
- [2025-08-27T20:19:33+00:00] Covered router sanitization and logging checks.
---
# Agent Log
- Added test_mission_neo4j_roundtrip.py to verify MissionDAG persistence.
## Agent Interaction
**Timestamp:** 2025-01-14T00:00:00
**Agent ID:** meta_update
**Team:** knowledge
**Action/Message:**
Added integration test verifying memory and knowledge graph persistence across mission steps
**Associated Data:**
```json
{"files": ["test_mission_step_persistence.py"]}- Added tests for BlackTeamOrchestrator context filtering.
## Agent Log 2025-09-06
- Fixed stray class definition in conftest.py causing IndentationError during pytest setup.
{"files": ["test_mission_step_persistence.py"]}\n## Agent Log 2025-09-06\n- Added tests covering WhiteGate gating behavior in multi-team orchestrator.\n
## Agent Log 2025-09-06
- Added test_adversary_pair_critics to verify critic verdict storage and asynchronous review. File is long; consider splitting.
- Added tests for ExecutiveAgent sub-orchestrator spawning and SubOrchestrator specialist filtering.## Agent Log 2025-08-28
- Restored conftest.py and added create_model stub to pydantic mock.

**Timestamp:** 2025-08-28T02:28:19+00:00
**Agent ID:** openai-assistant
**Team:** tests
**Action/Message:**
```
Wrapped long lines in test_knowledge_query_get to satisfy flake8 E501.
File is quite long; consider archiving older entries soon.
```
**Associated Data:**
```
File: tests/test_knowledge_query_get.py
```
---
## Agent Log 2025-09-07
- Introduced in-memory Qdrant client and Redis stub in test configuration to remove external dependencies.
- Ran flake8 and pytest for vector store tests.

## Agent Log 2025-09-07
- Added dictionary-based Redis stub and synced Qdrant test client API with upstream.
- Expanded vector store tests with scope eviction case and reran flake8 and pytest.

## Agent Log 2025-09-07
- Improved docstrings for Redis and Qdrant stubs in `conftest.py` and added vector store tests for empty queries and invalid limits.
- Executed flake8 on vector store modules and ran focused pytest suite.

File is very long; subsequent entries recorded in `agent-2.md`.
## Agent Log 2025-09-07
- Added PerformanceTracker unit tests covering success and failure retries.
- Stubbed ecosystem and team agents in conftest to resolve import cycles.
    # Add a dummy mission
    mission_history["test-mission"] = {"status": "completed"}
    response = client.get("/missions/history")
    assert response.status_code == 200
    assert "test-mission" in response.json()
## Agent Interaction
**Timestamp:** $(date -Iseconds)
**Agent ID:** openai-assistant
**Team:** tests
**Action/Message:**
```
Added unit tests for Galaxy Model backend including endpoint, extraction, and confidence calculation.
```
**Associated Data:**
```
Files: test_galaxy_backend.py
```
