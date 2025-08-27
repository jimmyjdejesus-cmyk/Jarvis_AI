import os
from fastapi.testclient import TestClient
from app.main import app


def test_set_neo4j_config(monkeypatch):
    os.environ["JARVIS_API_KEY"] = "test-key"
    captured = {}

    class DummyNeo4j:
        def __init__(self, uri, user, password):
            captured["uri"] = uri
            captured["user"] = user
            captured["password"] = password
        def is_alive(self):
            return True

    monkeypatch.setattr("app.main.Neo4jGraph", DummyNeo4j)
    import app.main as main
    monkeypatch.setattr(main, "neo4j_graph", None)
    client = TestClient(app)
    resp = client.post(
        "/api/neo4j/config",
        headers={"X-API-Key": "test-key"},
        json={"uri": "bolt://test", "user": "u", "password": "p"},
    )
    assert resp.status_code == 200
    assert captured["uri"] == "bolt://test"
    assert captured["user"] == "u"
    assert captured["password"] == "p"
