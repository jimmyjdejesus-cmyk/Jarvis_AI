from fastapi.testclient import TestClient

import importlib
import types
from pathlib import Path

jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "jarvis")]
import sys
sys.modules.setdefault("jarvis", jarvis_pkg)

from unittest.mock import patch

# Use patch.dict to inject "jarvis" into sys.modules only when needed
jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "jarvis")]

with patch.dict("sys.modules", {"jarvis": jarvis_pkg}):
    hub = importlib.import_module("jarvis.plugin_hub.hub")

app = hub.app
_installed_plugins = hub._installed_plugins


def login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_list_plugins_requires_auth():
    _installed_plugins.clear()
    client = TestClient(app)
    token = login(client, "user", "user")
    res = client.get("/api/plugins", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json() == []


def test_install_plugin_admin(monkeypatch):
    _installed_plugins.clear()
    client = TestClient(app)
    token = login(client, "admin", "admin")
    class Dummy:
        stdout = "[]"

    def fake_run(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr("jarvis.plugin_hub.hub.subprocess.run", fake_run)
    res = client.post(
        "/api/plugins/install",
        headers={"Authorization": f"Bearer {token}"},
        data={"name": "demo", "version": "0.1", "description": "Demo", "author": "me", "dependencies": ""},
    )
    assert res.status_code == 200
    assert _installed_plugins["demo"]["version"] == "0.1"


def test_moderation_flow(monkeypatch):
    _installed_plugins.clear()
    client = TestClient(app)
    user_token = login(client, "user", "user")
    admin_token = login(client, "admin", "admin")

    submit_res = client.post(
        "/api/plugins/submit",
        headers={"Authorization": f"Bearer {user_token}"},
        data={"name": "sub", "description": "", "author": ""},
    )
    submission_id = submit_res.json()["submission_id"]

    pend = client.get("/api/moderation/pending", headers={"Authorization": f"Bearer {admin_token}"})
    assert any(s["id"] == submission_id for s in pend.json())

    class Dummy:
        stdout = "[]"

    def fake_run(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr("jarvis.plugin_hub.hub.subprocess.run", fake_run)
    approve = client.post(
        "/api/moderation/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={"submission_id": submission_id},
    )
    assert approve.status_code == 200
    assert "sub" in _installed_plugins


def test_publish_plugin_with_publisher_role(monkeypatch):
    _installed_plugins.clear()
    client = TestClient(app)
    publisher_token = login(client, "publisher", "publisher")
    user_token = login(client, "user", "user")
    class Dummy:
        stdout = "[]"

    def fake_run(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr("jarvis.plugin_hub.hub.subprocess.run", fake_run)

    res = client.post(
        "/api/plugins/publish",
        headers={"Authorization": f"Bearer {publisher_token}"},
        data={"name": "demo", "version": "0.1", "url": "demo==0.1"},
    )
    assert res.status_code == 200
    assert _installed_plugins["demo"]["version"] == "0.1"

    res_forbidden = client.post(
        "/api/plugins/publish",
        headers={"Authorization": f"Bearer {user_token}"},
        data={"name": "demo2", "version": "0.1", "url": "demo2==0.1"},
    )
    assert res_forbidden.status_code == 403
