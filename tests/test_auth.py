from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_admin_access_logs():
    response = client.post(
        "/token", data={"username": "alice", "password": "secret"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    res = client.get(
        "/api/logs", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200

def test_non_admin_forbidden():
    response = client.post(
        "/token", data={"username": "bob", "password": "secret"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    res = client.get(
        "/api/logs", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403

def test_invalid_credentials():
    response = client.post(
        "/token", data={"username": "alice", "password": "wrong"}
    )
    assert response.status_code == 400
