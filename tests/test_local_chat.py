# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



import os
import pytest
from fastapi.testclient import TestClient

# Disable API auth for tests if not configured
os.environ.setdefault("ADAPTIVEMIND_DISABLE_AUTH", "true")
os.environ.setdefault("ADAPTIVEMIND_AUTH_SECRET", "test-secret")

# Skip this test if the legacy runtime isn't available (we archived it)
legacy_app = pytest.importorskip("legacy.app", reason="legacy runtime archived; enable if you need legacy tests")
legacy_main = getattr(legacy_app, "main", None)
if legacy_main is None:
    pytest.skip("legacy.main not present in archived legacy package")


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
