//... (existing tests above) ...

def test_push_and_recall(tmp_path):
    bus = MemoryBus(tmp_path)
    memory = ReplayMemory(capacity=10, memory_bus=bus)
    memory.push("s1", "a1", 1.0, "s2", False)
    memory.push("s1", "a2", 0.5, "s3", True)
    recalled = memory.recall("s1", top_k=2)
    assert len(recalled) == 2
    assert recalled[0][1] == "a2"
    assert recalled[1][1] == "a1"
    log_content = bus.read_log()
    assert "push" in log_content
    assert "recall" in log_content


def test_workflow_state_is_per_instance(monkeypatch):
    """Ensure workflow data is isolated per FastAPI app instance."""
    os.environ["JARVIS_API_KEY"] = "test-key"
    import app.main as main_module
    dummy = type("Dummy", (), {"child_orchestrators": []})()
    monkeypatch.setattr(main_module, "cerebro_orchestrator", dummy)
    monkeypatch.setattr(main_module, "specialist_agents", {})
    monkeypatch.setattr(main_module, "active_orchestrators", {})
    session_id = "session-test"
    headers = {"X-API-Key": "test-key"}
    with TestClient(main_module.app) as client1:
        resp = client1.get(f"/api/workflow/{session_id}", headers=headers)
        assert resp.status_code == 200
        assert session_id in client1.app.state.workflows_db
    with TestClient(main_module.app) as client2:
        assert session_id not in client2.app.state.workflows_db


def test_mission_history_endpoint(tmp_path):
    os.environ["JARVIS_API_KEY"] = "test-key"
    mission_id = "mission1"

    class DummySessionManager:
        def __init__(self, base_dir: str) -> None:
            self.base = Path(base_dir)

        def read_runs(self, mission_id: str):
            #...(the rest of the test code continues here)...