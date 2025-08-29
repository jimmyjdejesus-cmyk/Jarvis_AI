"""Authentication and authorization endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_token_missing_credentials():
    """Missing credentials return validation error."""
    response = client.post("/token")
    assert response.status_code == 422


def test_token_invalid_credentials():
    """Invalid credentials return unauthorized error."""
    response = client.post(
        "/token", data={"username": "bad", "password": "userpass"}
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_secret_endpoint_unauthenticated():
    """Accessing secret without token returns 401."""
    response = client.get("/secret")
    assert response.status_code == 401


def test_secret_endpoint_insufficient_role():
    """User token lacking admin role returns 403."""
    token_response = client.post(
        "/token", data={"username": "user", "password": "userpass"}
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/secret", headers=headers)
    assert response.status_code == 403


def test_secret_endpoint_with_admin_token():
    """Admin token grants access to the secret route."""
    token_response = client.post(
        "/token", data={"username": "admin", "password": "adminpass"}
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/secret", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"secret": "classified"}