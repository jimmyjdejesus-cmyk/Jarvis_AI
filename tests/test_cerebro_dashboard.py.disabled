import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from ui.cerebro import create_cerebro_app, CerebroDashboard
from fastapi.testclient import TestClient
from datetime import datetime


def test_cerebro_graph_and_metrics():
    dashboard = CerebroDashboard()
    app = create_cerebro_app(dashboard)
    client = TestClient(app)

    event_payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "info",
        "message": "node added",
        "correlation_id": "1",
        "data": {"id": "n1", "type": "Team", "label": "T"},
    }
    assert client.post("/event", json=event_payload).status_code == 200
    graph = client.get("/graph").json()
    assert graph["nodes"][0]["id"] == "n1"

    perf_payload = {"reward": 0.5, "tokens": 10, "probes": 2}
    assert client.post("/performance", json=perf_payload).status_code == 200
    metrics = client.get("/performance").json()
    assert metrics["average_reward"] == 0.5
    assert metrics["average_tokens"] == 10.0
    assert metrics["probe_policies"] == 2
