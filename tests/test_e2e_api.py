import pytest
from fastapi.testclient import TestClient

from jarvis_core import build_app
from jarvis_core.config import AppConfig, MonitoringConfig, PersonaConfig, SecurityConfig


@pytest.fixture(scope="module")
def test_client():
    config = AppConfig(
        personas={
            "generalist": PersonaConfig(
                name="generalist",
                description="Balanced assistant",
                system_prompt="You are a helpful assistant.",
                max_context_window=2048,
                routing_hint="general",
            ),
            "researcher": PersonaConfig(
                name="researcher",
                description="Deep research persona",
                system_prompt="Focus on sourcing and multi-step reasoning.",
                max_context_window=4096,
                routing_hint="research",
            ),
        },
        allowed_personas=["generalist", "researcher"],
        monitoring=MonitoringConfig(enable_metrics_harvest=False, harvest_interval_s=60.0),
    )
    app = build_app(config=config)
    with TestClient(app) as client:
        yield client


def _chat(client: TestClient, persona: str = "generalist"):
    payload = {
        "persona": persona,
        "messages": [{"role": "user", "content": "Summarise the latest context."}],
        "metadata": {"objective": "pytest"},
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["content"]
    assert data["tokens"] > 0
    return data


def test_health_endpoint(test_client: TestClient):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "degraded"}
    assert isinstance(data["available_models"], list)


def test_chat_generates_content(test_client: TestClient):
    data = _chat(test_client)
    assert "Persona focus" in data["content"]


def test_persona_switching(test_client: TestClient):
    research = _chat(test_client, persona="researcher")
    general = _chat(test_client, persona="generalist")
    assert research["content"] != general["content"]


def test_metrics_and_traces(test_client: TestClient):
    _chat(test_client)
    metrics = test_client.get("/api/v1/monitoring/metrics")
    traces = test_client.get("/api/v1/monitoring/traces")
    assert metrics.status_code == 200
    assert traces.status_code == 200
    assert isinstance(metrics.json()["history"], list)
    assert isinstance(traces.json()["traces"], list)


def test_api_key_required():
    config = AppConfig(
        personas={
            "generalist": PersonaConfig(
                name="generalist",
                description="",
                system_prompt="Stay factual.",
            )
        },
        allowed_personas=["generalist"],
        security=SecurityConfig(api_keys=["secret-key"]),
        monitoring=MonitoringConfig(enable_metrics_harvest=False, harvest_interval_s=60.0),
    )
    app = build_app(config=config)
    with TestClient(app) as client:
        denied = client.get("/api/v1/personas")
        assert denied.status_code == 401
        granted = client.get("/api/v1/personas", headers={"X-API-Key": "secret-key"})
        assert granted.status_code == 200
