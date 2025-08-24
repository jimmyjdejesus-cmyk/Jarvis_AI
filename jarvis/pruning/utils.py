"""Utility helpers for pruning workflow."""
from __future__ import annotations

from hashlib import sha256
from typing import Dict, Iterable, List


def path_signature(steps: Iterable[str], tools: Iterable[str], decisions: Iterable[str]) -> Dict[str, object]:
    """Create a deterministic signature for a path taken by a team."""
    key_items: List[str] = [*steps, *tools, *decisions]
    key = "|".join(key_items)[:4000]
    h = sha256(key.encode()).hexdigest()
    return {
        "hash": h,
        "steps": list(steps),
        "tools_used": list(tools),
        "key_decisions": list(decisions),
    }
