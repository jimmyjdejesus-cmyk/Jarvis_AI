"""Shared memory FastAPI service with scoped access.

This service combines basic key-value storage with more advanced
functionality for recording and querying execution paths, all secured
with principal verification and data masking.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from .vector_store import add_text, delete_text

app = FastAPI(title="SharedMemoryService")

# Nested dictionary principal -> scope -> key -> value
_memory: Dict[str, Dict[str, Dict[str, str]]] = {}
# Collected WS7 events for test inspection
EVENTS: List[Dict[str, str]] = []

# List of sensitive values that must be masked in events
SENSITIVE_VALUES: List[str] = []
SECRET_MASK = "***"


class MemoryItem(BaseModel):
    """Item stored in shared memory."""

    key: str
    value: str


def _mask(value: str) -> str:
    """Mask any sensitive substrings in ``value``."""
    for secret in SENSITIVE_VALUES:
        value = value.replace(secret, SECRET_MASK)
    return value


def _emit(event_type: str, principal: str, scope: str, key: Optional[str] = None) -> None:
    """Record an event following the WS7 structure, masking secrets."""
    event = {
        "version": "WS7",
        "type": _mask(event_type),
        "principal": _mask(principal),
        "scope": _mask(scope),
    }
    if key is not None:
        event["key"] = _mask(key)
    EVENTS.append(event)


def _verify_principal(request: Request, principal: str) -> None:
    """Ensure the caller principal matches the target principal."""
    caller = request.headers.get("X-Principal")
    if caller != principal:
        raise HTTPException(status_code=403, detail="Forbidden")


# ---------------------------------------------------------------------------
# Path recording and retrieval


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

    hash: Optional[str] = None
    steps: List[str]
    tools_used: List[str]
    key_decisions: List[str]
    metrics: Metrics
    outcome: Outcome
    scope: str
    citations: List[str] = []
    timestamp: float = Field(default_factory=lambda: time.time())


# Principal -> collection -> List[PathSignature]
_paths: Dict[str, Dict[str, List[PathSignature]]] = {}

# File to track project-wide path signatures
_PROJECT_LOG = Path(__file__).resolve().parent.parent / "agent_project.md"


def generate_hash(signature: PathSignature) -> str:
    """Generate a deterministic hash for a path signature."""
    hasher = hashlib.sha256()
    for part in signature.steps + signature.tools_used + signature.key_decisions:
        hasher.update(part.encode("utf-8"))
    return hasher.hexdigest()


def _log_project(signature: PathSignature) -> None:
    """Append the path hash and outcome to ``agent_project.md``."""
    line = f"- {signature.hash} {signature.outcome.result}\n"
    with _PROJECT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)


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
    sig = req.signature
    if not sig.hash:
        sig.hash = generate_hash(sig)
    store = _paths.setdefault(req.target, {}).setdefault(req.kind, [])
    store.append(sig)
    text = " ".join(sig.steps + sig.tools_used + sig.key_decisions)
    add_text(req.target, req.kind, sig.hash, text)
    if req.target == "project":
        _log_project(sig)
    _emit("path_record", req.actor, f"{req.target}:{req.kind}", sig.hash)
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


class NegativeCheck(BaseModel):
    actor: str
    target: str
    signature: PathSignature
    threshold: float = 0.5


@app.post("/paths/avoid")
def avoid_negative(req: NegativeCheck) -> Dict[str, object]:
    """Check project negative paths before branching."""
    _check_acl(req.actor, req.target, "negative", "read")
    results = query_paths(
        PathQuery(
            actor=req.actor,
            target=req.target,
            kind="negative",
            signature=req.signature,
            threshold=req.threshold,
        )
    )["results"]
    return {"avoid": bool(results), "results": results}


class PruneRequest(BaseModel):
    actor: str
    target: str
    ttl_seconds: int


@app.post("/paths/prune")
def prune_paths(req: PruneRequest) -> Dict[str, int]:
    """Prune stored paths older than ``ttl_seconds``."""
    _check_acl(req.actor, req.target, "positive", "write")
    cutoff = time.time() - req.ttl_seconds
    removed = 0
    store = _paths.get(req.target, {})
    for kind, sigs in list(store.items()):
        new_sigs: List[PathSignature] = []
        for sig in sigs:
            if sig.timestamp < cutoff:
                delete_text(req.target, kind, sig.hash)
                removed += 1
            else:
                new_sigs.append(sig)
        store[kind] = new_sigs
    return {"removed": removed}


# ---------------------------------------------------------------------------
# Basic key/value scoped memory operations
# Note: These endpoints are placed after the more specific /paths/ ones
# to prevent routing conflicts.


@app.post("/{principal}/{scope}")
def write_item(principal: str, scope: str, item: MemoryItem, request: Request) -> Dict[str, str]:
    """Write a key/value pair within a principal's scope."""
    _verify_principal(request, principal)
    store = _memory.setdefault(principal, {}).setdefault(scope, {})
    store[item.key] = item.value
    add_text(principal, scope, item.key, item.value)
    _emit("write", principal, scope, item.key)
    return {"status": "ok"}


@app.get("/{principal}/{scope}/hash")
def scope_hash(principal: str, scope: str, request: Request) -> Dict[str, str]:
    """Return a SHA256 hash of all entries in a scope."""
    _verify_principal(request, principal)
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
def read_item(principal: str, scope: str, key: str, request: Request) -> Dict[str, str]:
    """Read a value from scoped memory."""
    _verify_principal(request, principal)
    try:
        value = _memory[principal][scope][key]
    except KeyError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=404, detail="Not found") from exc
    _emit("read", principal, scope, key)
    return {"value": value}