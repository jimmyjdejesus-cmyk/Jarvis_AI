# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Shared pytest fixtures for the AdaptiveMind test suite.

This module provides reusable pytest fixtures that can be used across
different test modules to ensure consistent test setup and teardown.
"""

import os
import subprocess
import sys
import time
import warnings
from pathlib import Path
from unittest.mock import Mock
from typing import Dict, Any

import pytest

from .external_dependencies import MockNeo4jDriver, MockPydanticModel, MockNetworkX
from .api_mocks import MockHTTPClient, MockWebSocket
from .agent_mocks import MockAgent, MockOrchestrator, MockSpecialist


# Environment setup
os.environ.setdefault("ADAPTIVEMIND_TEST_MODE", "true")


@pytest.fixture
def client_fixture():
    """Mock HTTP client fixture for API tests."""
    return MockHTTPClient()


@pytest.fixture
def mock_environment():
    """Setup mock environment for tests."""
    # Ensure repository root on path
    ROOT = Path(__file__).resolve().parent.parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    
    # Setup test environment variables
    test_env = {
        "ADAPTIVEMIND_TEST_MODE": "true",
        "ADAPTIVEMIND_TEST_BASE_URL": "http://127.0.0.1:8000",
        "ADAPTIVEMIND_API_KEY": "test-api-key",
        "ADAPTIVEMIND_DATABASE_URL": "bolt://localhost:7687"
    }
    
    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_env
    
    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def test_server_fixture():
    """Start a lightweight test server for integration tests."""
    base = os.getenv("ADAPTIVEMIND_TEST_BASE_URL", "http://127.0.0.1:8000")
    
    # If a custom base URL is provided, assume an external server will be used
    if "127.0.0.1:8000" not in base:
        yield None
        return

    # If the backend is already serving at the expected base URL, do not
    # try to start a second server (CI starts its own backend). Check with
    # a quick HTTP GET; if 200 OK, assume the backend is available and skip
    # starting our lightweight test server.
    import urllib.request

    def _is_up(url: str) -> bool:
        try:
            req = urllib.request.Request(url.rstrip("/") + "/")
            with urllib.request.urlopen(req, timeout=1) as resp:
                return resp.status == 200
        except Exception:
            return False

    if _is_up(base):
        # Backend already running (e.g., CI) — nothing to do
        yield None
        return

    server_script = Path(__file__).parent.parent / "_test_server.py"
    proc = subprocess.Popen([sys.executable, str(server_script)])

    # Wait for the test server to be ready (with a short timeout)
    deadline = time.time() + 5
    while time.time() < deadline:
        if _is_up(base):
            break
        time.sleep(0.2)

    try:
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    return MockAgent(name="test_agent", agent_type="test")


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator with registered agents."""
    orchestrator = MockOrchestrator()
    
    # Register some test agents
    meta_agent = MockAgent(name="meta_agent", agent_type="meta")
    coding_agent = MockAgent(name="coding_agent", agent_type="coding")
    research_agent = MockAgent(name="research_agent", agent_type="research")
    
    orchestrator.register_agent(meta_agent)
    orchestrator.register_agent(coding_agent)
    orchestrator.register_agent(research_agent)
    
    # Register some test specialists
    specialist1 = MockSpecialist("specialist1", "text_generation")
    specialist2 = MockSpecialist("specialist2", "code_analysis")
    
    orchestrator.register_specialist(specialist1)
    orchestrator.register_specialist(specialist2)
    
    return orchestrator


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    return MockWebSocket()


@pytest.fixture
def mock_database():
    """Create a mock database driver for testing."""
    return MockNeo4jDriver()


@pytest.fixture
def mock_model():
    """Create a mock Pydantic model for testing."""
    return MockPydanticModel(name="test_model", value=42)


@pytest.fixture
def mock_graph():
    """Create a mock NetworkX graph for testing."""
    graph = MockNetworkX()
    # Add some test nodes and edges
    graph.add_node("node1", type="test")
    graph.add_node("node2", type="test")
    graph.add_edge("node1", "node2", weight=1.0)
    return graph


@pytest.fixture
def mock_specialist_registry():
    """Create a mock specialist registry for testing."""
    registry = {
        "text_generation": MockSpecialist("text_gen_1", "text_generation"),
        "code_analysis": MockSpecialist("code_analyzer_1", "code_analysis"),
        "data_processing": MockSpecialist("data_proc_1", "data_processing")
    }
    return registry


@pytest.fixture
def sample_api_response():
    """Provide a sample API response for testing."""
    return {
        "id": "chatcmpl-test-id",
        "object": "chat.completion",
        "created": 1640995200,
        "model": "llama3.2:latest",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a mock response for testing."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 15,
            "total_tokens": 25
        }
    }


@pytest.fixture
def sample_memory_data():
    """Provide sample memory data for testing."""
    return {
        "memory_id": "test_memory_001",
        "content": "This is a test memory for storage and retrieval.",
        "metadata": {
            "type": "test_memory",
            "created_by": "test_fixture",
            "tags": ["test", "sample"]
        },
        "timestamp": time.time()
    }


@pytest.fixture
def sample_workflow_data():
    """Provide sample workflow data for testing."""
    return {
        "workflow_name": "test_workflow",
        "steps": [
            {"name": "step1", "type": "agent_task", "agent": "meta_agent"},
            {"name": "step2", "type": "specialist_task", "specialist": "text_generation"},
            {"name": "step3", "type": "coordination_task", "coordinator": "meta_agent"}
        ],
        "inputs": {
            "user_request": "Test workflow execution",
            "context": {"test_mode": True}
        }
    }


@pytest.fixture
def warning_capture():
    """Capture warnings for testing."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        yield w


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for file operations."""
    return tmp_path


@pytest.fixture
def cleanup_globals():
    """Cleanup global state after test."""
    # Store original state
    original_state = {}
    
    yield
    
    # Cleanup any global state changes
    # This is a placeholder for any global cleanup needed


@pytest.fixture(scope="session")
def session_test_data():
    """Session-scoped test data that persists across tests."""
    return {
        "test_session_id": "test_session_123",
        "created_at": time.time(),
        "test_counter": 0
    }


@pytest.fixture(autouse=True)
def auto_cleanup():
    """Automatically cleanup after each test."""
    # This fixture runs automatically for all tests
    # Add any cleanup logic here if needed
    yield
    # Cleanup logic after test


# Parameterized fixtures for different test scenarios
@pytest.fixture(params=["small", "medium", "large"])
def request_size(request):
    """Parametrized fixture for different request sizes."""
    sizes = {
        "small": {"text": "Short test request", "expected_tokens": 5},
        "medium": {"text": "This is a medium length test request for comprehensive testing", "expected_tokens": 15},
        "large": {"text": "This is a very long test request " * 10, "expected_tokens": 100}
    }
    return sizes[request.param]


@pytest.fixture(params=["json", "xml", "text"])
def response_format(request):
    """Parametrized fixture for different response formats."""
    formats = {
        "json": {"content_type": "application/json", "parser": lambda x: x},
        "xml": {"content_type": "application/xml", "parser": lambda x: x},
        "text": {"content_type": "text/plain", "parser": lambda x: x}
    }
    return formats[request.param]


# Performance testing fixtures
@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
            self.start_time = None
        
        def start_timer(self, operation_name: str):
            """Start timing an operation."""
            self.metrics[operation_name] = {"start": time.time()}
        
        def end_timer(self, operation_name: str):
            """End timing an operation."""
            if operation_name in self.metrics:
                end_time = time.time()
                duration = end_time - self.metrics[operation_name]["start"]
                self.metrics[operation_name]["duration"] = duration
                self.metrics[operation_name]["end"] = end_time
        
        def get_metrics(self) -> Dict[str, Any]:
            """Get all collected metrics."""
            return self.metrics.copy()
        
        def reset(self):
            """Reset all metrics."""
            self.metrics = {}
    
    return PerformanceMonitor()


# Validation fixtures
@pytest.fixture
def validation_helper():
    """Provide validation helper methods for tests."""
    class ValidationHelper:
        @staticmethod
        def validate_api_response(response: Dict[str, Any], required_fields: list):
            """Validate API response structure."""
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            return True
        
        @staticmethod
        def validate_agent_response(response: Dict[str, Any]):
            """Validate agent response structure."""
            required_fields = ["response", "tokens_generated", "avg_confidence"]
            return ValidationHelper.validate_api_response(response, required_fields)
        
        @staticmethod
        def validate_health_status(health_data: Dict[str, Any]):
            """Validate health check response structure."""
            required_fields = ["status", "timestamp"]
            return ValidationHelper.validate_api_response(health_data, required_fields)
    
    return ValidationHelper()


__all__ = [
    "client_fixture",
    "mock_environment", 
    "test_server_fixture",
    "mock_agent",
    "mock_orchestrator",
    "mock_websocket",
    "mock_database",
    "mock_model",
    "mock_graph",
    "mock_specialist_registry",
    "sample_api_response",
    "sample_memory_data",
    "sample_workflow_data",
    "warning_capture",
    "temp_dir",
    "cleanup_globals",
    "session_test_data",
    "auto_cleanup",
    "request_size",
    "response_format",
    "performance_monitor",
    "validation_helper"
]
