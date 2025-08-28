from fastapi.testclient import TestClient
import os

from app.main import app


def test_set_credential(monkeypatch):
    monkeypatch.setenv("JARVIS_API_KEY", "test-key")
    client = TestClient(app)
    resp = client.post(
        "/api/credentials",
        headers={"X-API-Key": "test-key"},
        json={"service": "OPENAI_API_KEY", "value": "abc"},
    )
    assert resp.status_code == 200
    assert os.environ["OPENAI_API_KEY"] == "abc"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_set_credential_invalid_service(monkeypatch):
    monkeypatch.setenv("JARVIS_API_KEY", "test-key")
    client = TestClient(app)
    resp = client.post(
        "/api/credentials",
        headers={"X-API-Key": "test-key"},
        json={"service": "UNKNOWN", "value": "x"},
    )
    assert resp.status_code == 400
