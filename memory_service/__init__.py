"""Shared memory FastAPI service with scoped access."""

from __future__ import annotations

import hashlib
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .vector_store import add_text

app = FastAPI(title="SharedMemoryService")

# Nested dictionary principal -> scope -> key -> value
_memory: Dict[str, Dict[str, Dict[str, str]]] = {}
# Collected WS7 events for test inspection
EVENTS: List[Dict[str, str]] = []


class MemoryItem(BaseModel):
    """Item stored in shared memory."""

    key: str
    value: str


class Metrics(BaseModel):
    """Performance metrics associated with a path."""

    novelty: float
    growth: float
    cost: float


class Outcome(BaseModel):
    """Outcome of a path execution."""

    result: str  # "pass" or "fail"


class PathSignature(BaseModel):
    """Signature capturing important aspects of a path."""

    hash: str
    steps: List[str]
    tools_used: List[str]
    key_decisions: List[str]
    metrics: Metrics
    outcome: Outcome
    scope: str
    citations: List[str] = []


# Principal -> collection -> List[PathSignature]
_paths: Dict[str, Dict[str, List[PathSignature]]] = {}


def _emit(event_type: str, principal: str, scope: str, key: Optional[str] = None) -> None:
    """Record an event following the WS7 structure."""
    event = {
        "version": "WS7",
        "type": event_type,
        "principal": principal,
        "scope": scope,
    }
    if key is not None:
        event["key"] = key
    EVENTS.append(event)




# ---------------------------------------------------------------------------
# Path recording and retrieval


def _check_acl(actor: str, target: str, kind: str, op: str) -> None:
    """Very small ACL layer for path collections."""
    if target == "project":
        if op == "write" and actor not in {"meta", "orchestrator"}:
            raise HTTPException(status_code=403, detail="ACL violation")
        if op == "read" and kind == "negative" and actor.startswith("team/"):
            return
        if actor in {"meta", "orchestrator"}:
            return
        raise HTTPException(status_code=403, detail="ACL violation")
    if target.startswith("team/"):
        if actor == target:
            return
        raise HTTPException(status_code=403, detail="ACL violation")
    raise HTTPException(status_code=403, detail="ACL violation")


class PathRecord(BaseModel):
    actor: str
    target: str
    kind: str  # positive | negative | local
    signature: PathSignature


@app.post("/paths/record")
def record_path(req: PathRecord) -> Dict[str, str]:
    """Record a path signature in the shared service."""
    _check_acl(req.actor, req.target, req.kind, "write")
    store = _paths.setdefault(req.target, {}).setdefault(req.kind, [])
    store.append(req.signature)
    text = " ".join(
        req.signature.steps
        + req.signature.tools_used
        + req.signature.key_decisions
    )
    add_text(req.target, req.kind, req.signature.hash, text)
    EVENTS.append(
        {
            "version": "WS7",
            "type": "path_record",
            "principal": req.actor,
            "scope": f"{req.target}:{req.kind}",
            "key": req.signature.hash,
        }
    )
    return {"status": "ok"}


def _similarity(a: PathSignature, b: PathSignature) -> float:
    aset, bset = set(a.steps), set(b.steps)
    if not aset and not bset:
        return 0.0
    return len(aset & bset) / len(aset | bset)


class PathQuery(BaseModel):
    actor: str
    target: str
    kind: str
    signature: PathSignature
    threshold: float = 0.5


@app.post("/paths/query")
def query_paths(req: PathQuery) -> Dict[str, List[Dict[str, object]]]:
    """Return similar path signatures from memory."""
    _check_acl(req.actor, req.target, req.kind, "read")
    matches: List[Tuple[float, PathSignature]] = []
    for sig in _paths.get(req.target, {}).get(req.kind, []):
        score = _similarity(req.signature, sig)
        if score >= req.threshold:
            matches.append((score, sig))
    matches.sort(key=lambda x: x[0], reverse=True)
    results = [
        {"similarity": score, "signature": sig.dict()} for score, sig in matches
    ]
    return {"results": results}


# ---------------------------------------------------------------------------
# Basic key/value scoped memory operations (kept after path endpoints to avoid
# routing collisions).


@app.post("/{principal}/{scope}")
def write_item(principal: str, scope: str, item: MemoryItem) -> Dict[str, str]:
    """Write a key/value pair within a principal's scope."""
    store = _memory.setdefault(principal, {}).setdefault(scope, {})
    store[item.key] = item.value
    add_text(principal, scope, item.key, item.value)
    _emit("write", principal, scope, item.key)
    return {"status": "ok"}


@app.get("/{principal}/{scope}/hash")
def scope_hash(principal: str, scope: str) -> Dict[str, str]:
    """Return a SHA256 hash of all entries in a scope."""
    scope_data = _memory.get(principal, {}).get(scope)
    if scope_data is None:
        raise HTTPException(status_code=404, detail="Not found")
    hasher = hashlib.sha256()
    for k in sorted(scope_data):
        hasher.update(k.encode("utf-8"))
        hasher.update(scope_data[k].encode("utf-8"))
    digest = hasher.hexdigest()
    _emit("hash", principal, scope)
    return {"hash": digest}


@app.get("/{principal}/{scope}/{key}")
def read_item(principal: str, scope: str, key: str) -> Dict[str, str]:
    """Read a value from scoped memory."""
    try:
        value = _memory[principal][scope][key]
    except KeyError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=404, detail="Not found") from exc
    _emit("read", principal, scope, key)
    return {"value": value}
