# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



import os
import time
import json
import pytest
import requests

BASE_URL = os.getenv("JARVIS_TEST_BASE_URL", "http://127.0.0.1:8000")
REQUIRE_NEW_RUNTIME = os.getenv("REQUIRE_NEW_RUNTIME", "false").lower() in {"1", "true", "yes", "on"}


def _get(path: str, timeout: int = 15):
    return requests.get(f"{BASE_URL}{path}", timeout=timeout)


def _post(path: str, payload=None, timeout: int = 30):
    return requests.post(f"{BASE_URL}{path}", json=payload, timeout=timeout)


def _assert_status(resp):
    if REQUIRE_NEW_RUNTIME:
        assert resp.status_code == 200
    else:
        assert resp.status_code in (200, 503)


def test_security_stats_and_events():
    r = _get("/api/security/stats")
    _assert_status(r)
    if r.status_code == 200:
        data = r.json()
        assert "total_events" in data
        r2 = _get("/api/security/events?limit=10")
        _assert_status(r2)


def test_security_validate_and_audit():
    payload = {"agent_id": "research_agent", "action": "read", "context": {"test": True}}
    r = _post("/api/security/validate", payload)
    _assert_status(r)
    r2 = _post("/api/security/audit")
    _assert_status(r2)


def test_monitoring_health_and_metrics():
    r = _get("/api/monitoring/health")
    _assert_status(r)
    r2 = _get("/api/monitoring/metrics")
    _assert_status(r2)


def test_monitoring_summary_and_performance():
    r = _get("/api/monitoring/summary?time_window_minutes=10")
    _assert_status(r)
    r2 = _get("/api/monitoring/performance")
    _assert_status(r2)


def test_monitoring_export():
    r = _get("/api/monitoring/export?format=json")
    _assert_status(r)
