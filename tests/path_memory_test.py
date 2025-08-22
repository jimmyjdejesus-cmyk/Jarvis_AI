from __future__ import annotations

from fastapi.testclient import TestClient

from memory_service import app


def _sample_signature(hash_val: str) -> dict:
    return {
        "hash": hash_val,
        "steps": ["step1", "step2"],
        "tools_used": ["tool"],
        "key_decisions": ["dec"],
        "metrics": {"novelty": 0.1, "growth": 0.2, "cost": 0.3},
        "outcome": {"result": "fail"},
        "scope": "demo",
        "citations": [],
    }


def test_path_acl_and_query() -> None:
    client = TestClient(app)

    sig1 = _sample_signature("1")
    # orchestrator writes to project positive
    resp = client.post(
        "/paths/record",
        json={
            "actor": "orchestrator",
            "target": "project",
            "kind": "positive",
            "signature": sig1,
        },
    )
    assert resp.status_code == 200

    # team cannot write project negative
    sig2 = _sample_signature("2")
    resp = client.post(
        "/paths/record",
        json={
            "actor": "team/red",
            "target": "project",
            "kind": "negative",
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
            "kind": "local",
            "signature": sig2,
        },
    )
    assert resp.status_code == 200

    # orchestrator records project negative
    sig3 = _sample_signature("3")
    resp = client.post(
        "/paths/record",
        json={
            "actor": "orchestrator",
            "target": "project",
            "kind": "negative",
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
    assert results and results[0]["signature"]["hash"] == "3"

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
