from __future__ import annotations

from typing import Any

import pytest

from jarvis.tools.github import create_issue


class DummyResponse:
    def __init__(self, payload: dict[str, Any]):
        self._payload = payload
        self.raise_for_status_called = False

    def json(self) -> dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        self.raise_for_status_called = True


def test_create_issue_success(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResponse({"id": 1})

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setattr("requests.post", fake_post)
    result = create_issue("owner/repo", "title", "body")
    assert result["id"] == 1


def test_create_issue_missing_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValueError):
        create_issue("owner/repo", "title", "body")
