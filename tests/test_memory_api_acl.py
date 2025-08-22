from __future__ import annotations

from fastapi.testclient import TestClient

from memory_service import app


def test_cross_principal_access_blocked() -> None:
    client = TestClient(app)
    # write as alice
    resp = client.post(
        "/alice/notes",
        json={"key": "greeting", "value": "hi"},
        headers={"X-Principal": "alice"},
    )
    assert resp.status_code == 200
    # read as same principal allowed
    resp = client.get(
        "/alice/notes/greeting", headers={"X-Principal": "alice"}
    )
    assert resp.status_code == 200
    assert resp.json()["value"] == "hi"
    # read as different principal blocked
    resp = client.get(
        "/alice/notes/greeting", headers={"X-Principal": "bob"}
    )
    assert resp.status_code == 403
