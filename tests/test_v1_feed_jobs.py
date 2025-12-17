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

BASE_URL = os.getenv("ADAPTIVEMIND_TEST_BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("ADAPTIVEMIND_API_KEY", "test-key")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
REQUIRE_NEW_RUNTIME = os.getenv("REQUIRE_NEW_RUNTIME", "false").lower() in {"1", "true", "yes", "on"}


def _assert_status(resp):
    if REQUIRE_NEW_RUNTIME:
        assert resp.status_code == 200, f"Expected 200 got {resp.status_code}: {resp.text}"
    else:
        # For jobs, 200 expected on submission; feed is independent
        assert resp.status_code in (200,), f"Unexpected status code {resp.status_code}: {resp.text}"


def test_v1_feed_ingest():
    url = f"{BASE_URL}/api/v1/feed/ingest"
    payload = {"items": [{"source": "pytest", "content": "Feed content from test", "metadata": {"subject": "test"}}]}
    r = requests.post(url, headers=HEADERS, data=json.dumps(payload), timeout=20)
    _assert_status(r)
    data = r.json()
    assert "ingested" in data


def test_v1_jobs_chat_and_status():
    submit_url = f"{BASE_URL}/api/v1/jobs"
    payload = {"mode": "chat", "payload": {"messages": [{"role": "user", "content": "Hello via job"}]}}
    r = requests.post(submit_url, headers=HEADERS, data=json.dumps(payload), timeout=20)
    assert r.status_code == 200, f"Job submission failed: {r.status_code} {r.text}"
    job_id = r.json().get("job_id")
    assert job_id

    # Poll status
    status_url = f"{BASE_URL}/api/v1/jobs/{job_id}"
    deadline = time.time() + 30
    while time.time() < deadline:
        s = requests.get(status_url, headers=HEADERS, timeout=10)
        assert s.status_code == 200
        sd = s.json()
        if sd.get("status") in ("completed", "failed"):
            break
        time.sleep(1)
    assert sd.get("status") in ("completed", "failed")
