import asyncio
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))
from jarvis.orchestration.server import app, bus


def test_poll_events_endpoint():
    client = TestClient(app)
    asyncio.run(
        bus.publish(
            "demo", {"a": 1}, scope="runx", run_id="runx", step_id="s1", parent_id=None
        )
    )
    resp = client.get("/events/runx")
    assert resp.status_code == 200
    data = resp.json()
    assert data and data[0]["run_id"] == "runx" and data[0]["step_id"] == "s1"
