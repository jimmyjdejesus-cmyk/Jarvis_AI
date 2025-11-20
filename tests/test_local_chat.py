import os
import pytest
from fastapi.testclient import TestClient

# Disable API auth for tests if not configured
os.environ.setdefault("JARVIS_DISABLE_AUTH", "true")
os.environ.setdefault("JARVIS_AUTH_SECRET", "test-secret")

from legacy.app import main as legacy_main


@pytest.fixture
def legacy_client():
    app = legacy_main.app
    with TestClient(app) as client:
        yield client


def test_local_chat_endpoint(legacy_client):
    payload = {
        "messages": [{"role": "user", "content": "What is Python?"}],
        "model": None,
        "temperature": 0.7,
        "max_tokens": 128,
    }
    response = legacy_client.post("/api/v1/local_chat", json=payload)
    # The endpoint may be unavailable if Ollama isn't running; Accept 200 or 503
    assert response.status_code in {200, 503}
    if response.status_code == 200:
        data = response.json()
        assert "content" in data
        assert data.get("model") in {"ollama", None}
