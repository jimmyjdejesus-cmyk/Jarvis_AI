# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



import os
import pytest
import requests

BASE_URL = os.getenv("ADAPTIVEMIND_TEST_BASE_URL", "http://127.0.0.1:8000")
REQUIRE_NEW_RUNTIME = os.getenv("REQUIRE_NEW_RUNTIME", "false").lower() in {"1", "true", "yes", "on"}


def _get(path: str, timeout: int = 15):
    return requests.get(f"{BASE_URL}{path}", timeout=timeout)


def _post(path: str, payload=None, timeout: int = 30):
    return requests.post(f"{BASE_URL}{path}", json=payload, timeout=timeout)


def _assert_status(resp):
    if REQUIRE_NEW_RUNTIME:
        assert resp.status_code == 200
    else:
        assert resp.status_code in (200, 503, 400)


def test_memory_stats_and_knowledge_search():
    r = _get("/api/memory/stats")
    _assert_status(r)
    r2 = _get("/api/knowledge/search?q=pytest")
    _assert_status(r2)


def test_memory_sync_and_migrate():
    r = _post("/api/memory/sync/to-legacy")
    _assert_status(r)
    r2 = _post("/api/memory/migrate")
    _assert_status(r2)


def test_workflow_capabilities_and_active():
    r = _get("/api/workflows/capabilities")
    _assert_status(r)
    r2 = _get("/api/workflows/active")
    _assert_status(r2)
