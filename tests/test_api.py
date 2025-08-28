# ... (existing tests above) ...

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.test_harness import create_test_app
from jarvis.memory.memory_bus import MemoryBus
from jarvis.memory.replay_memory import Experience, ReplayMemory


def test_push_and_recall(tmp_path: Path) -> None:
    memory = ReplayMemory(capacity=10, log_dir=str(tmp_path))
    memory.add(Experience("s1", "a1", 1.0, "s2", False))
    memory.add(Experience("s1", "a2", 0.5, "s3", True))
    recalled = memory.recall("s1", top_k=2)
    assert len(recalled) == 2
    assert recalled[0].action == "a2"
    assert recalled[1].action == "a1"
    bus = MemoryBus(tmp_path)
    log_content = bus.read_log()
    assert "Inserted experience" in log_content
    assert "Recall experience" in log_content


def test_workflow_state_is_per_instance() -> None:
    """Ensure workflow data is isolated per FastAPI app instance."""
    os.environ["JARVIS_API_KEY"] = "test-key"

    def create_app() -> FastAPI:
        app = FastAPI()
        app.state.workflows_db = {}

        @app.get("/api/workflow/{session_id}")
        def get_workflow(session_id: str):  # pragma: no cover - simple stub
            app.state.workflows_db[session_id] = {}
            return {"id": session_id}

        return app

    session_id = "session-test"
    headers = {"X-API-Key": "test-key"}
    with TestClient(create_app()) as client1:
        resp = client1.get(f"/api/workflow/{session_id}", headers=headers)
        assert resp.status_code == 200
        assert session_id in client1.app.state.workflows_db
    with TestClient(create_app()) as client2:
        assert session_id not in client2.app.state.workflows_db


def test_mission_history_endpoint() -> None:
    mission_id = "mission1"

    class DummyGraph:
        def get_mission_history(self, mid: str):
            assert mid == mission_id
            return {"id": mid, "steps": []}

        def is_alive(self) -> bool:
            return True

    app = create_test_app(DummyGraph())
    with TestClient(app) as client:
        resp = client.get(f"/missions/{mission_id}/history")
        assert resp.status_code == 200
        assert resp.json() == {"id": mission_id, "steps": []}

