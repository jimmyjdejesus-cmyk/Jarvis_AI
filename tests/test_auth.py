from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def get_token(username: str, password: str) -> str:
    """Helper function to get a JWT token."""
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_access_logs():
    """Verify that an admin user can access the logs endpoint."""
    token = get_token("admin", "adminpass")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/logs", headers=headers)
    assert response.status_code == 200


def test_user_forbidden_logs():
    """Verify that a non-admin user is forbidden from accessing the logs endpoint."""
    token = get_token("user", "userpass")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/logs", headers=headers)
    assert response.status_code == 403


def test_invalid_credentials():
    """Verify that invalid credentials result in a 400 Bad Request."""
    response = client.post("/token", data={"username": "alice", "password": "wrong"})
    assert response.status_code == 400


def test_workflow_requires_auth():
    """Verify that the workflow endpoint requires a valid JWT token."""
    response = client.get("/api/workflow/test")
    assert response.status_code == 401