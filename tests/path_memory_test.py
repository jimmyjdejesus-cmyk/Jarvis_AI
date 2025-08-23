from __future__ import annotations

import time
import pathlib
import sys

from fastapi.testclient import TestClient

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
from memory_service import PathSignature, app, generate_hash


def _sample_signature(score: float, ts: float | None = None) -> dict:
    sig = {
        "steps": ["step1", "step2"],
        "tools_used": ["tool"],
        "key_decisions": ["dec"],
        "embedding": [],
        "metrics": {"novelty": 0.1, "growth": 0.2, "cost": 0.3},
        "outcome": {"result": "pass" if score >= 0.5 else "fail", "oracle_score": score},
        "scope": "demo",
        "citations": [],
    }
    if ts is not None:
        sig["timestamp"] = ts
    return sig


def test_path_acl_and_query() -> None:
    client = TestClient(app)

    sig1 = _sample_signature(0.95)
    # orchestrator writes to project positive
    resp = client.post(
        "/paths/record",
        json={
            "actor": "orchestrator",
            "target": "project",
            "signature": sig1,
        },
    )
    assert resp.status_code == 200

    expected_hash = generate_hash(PathSignature(**sig1))

    # team cannot write project negative
    sig2 = _sample_signature(0.1)
    resp = client.post(
        "/paths/record",
        json={
            "actor": "team/red",
            "target": "project",
            "signature": sig2,
        },
    )
    assert resp.status_code == 403

    # team writes to own local
    resp = client.post(
        "/paths/record",
        json={
            "actor": "team/red",
            "target": "team/red",
            "signature": sig2,
        },
    )
    assert resp.status_code == 200

    # orchestrator records project negative
    sig3 = _sample_signature(0.1)
    resp = client.post(
        "/paths/record",
        json={
            "actor": "orchestrator",
            "target": "project",
            "signature": sig3,
        },
    )
    assert resp.status_code == 200

    # team can query project negative
    resp = client.post(
        "/paths/query",
        json={
            "actor": "team/red",
            "target": "project",
            "kind": "negative",
            "signature": sig3,
            "threshold": 0.0,
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert results and results[0]["signature"]["hash"] == generate_hash(PathSignature(**sig3))

    # team cannot query project positive
    resp = client.post(
        "/paths/query",
        json={
            "actor": "team/red",
            "target": "project",
            "kind": "positive",
            "signature": sig1,
        },
    )
    assert resp.status_code == 403

    # orchestrator queries project positive and gets hash
    resp = client.post(
        "/paths/query",
        json={
            "actor": "orchestrator",
            "target": "project",
            "kind": "positive",
            "signature": sig1,
            "threshold": 0.0,
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert results and results[0]["signature"]["hash"] == expected_hash


def test_negative_lookup_and_prune() -> None:
    client = TestClient(app)

    sig = _sample_signature(0.1)
    client.post(
        "/paths/record",
        json={
            "actor": "orchestrator",
            "target": "project",
            "signature": sig,
        },
    )

    # team checks for negative paths before branching
    resp = client.post(
        "/paths/avoid",
        json={
            "actor": "team/red",
            "target": "project",
            "signature": sig,
            "threshold": 0.0,
        },
    )
    data = resp.json()
    assert resp.status_code == 200 and data["avoid"] is True

    # record an old path and prune it
    old_ts = time.time() - 100
    old_sig = _sample_signature(0.95, ts=old_ts)
    client.post(
        "/paths/record",
        json={
            "actor": "orchestrator",
            "target": "project",
            "signature": old_sig,
        },
    )

    resp = client.post(
        "/paths/prune",
        json={"actor": "orchestrator", "target": "project", "ttl_seconds": 50},
    )
    assert resp.status_code == 200
    assert resp.json()["removed"] >= 1
