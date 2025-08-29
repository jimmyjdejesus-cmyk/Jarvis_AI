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


def test_get_mission_history():
    """Test mission history retrieval via the API."""
    test_app = create_test_app(mission_history)
    client = TestClient(test_app)

    # Add a dummy mission
    mission_history["test-mission"] = {"status": "completed"}

    response = client.get("/missions/history")
    assert response.status_code == 200
    assert "test-mission" in response.json()