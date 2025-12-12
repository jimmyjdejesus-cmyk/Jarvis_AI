"""Minimal ProjectMemory shim for tests.

The real project memory is complex and depends on external storage.
This lightweight shim provides a small API surface so unit tests that
import `jarvis.memory.project_memory.ProjectMemory` can run.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class ProjectMemory:
    def __init__(self) -> None:
        # store simple key -> list of entries
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def add_entry(self, key: str, entry: Dict[str, Any]) -> None:
        self._store.setdefault(key, []).append(entry)

    def query(self, key: str) -> List[Dict[str, Any]]:
        return list(self._store.get(key, []))

    def clear(self, key: Optional[str] = None) -> None:
        if key is None:
            self._store.clear()
        else:
            self._store.pop(key, None)
