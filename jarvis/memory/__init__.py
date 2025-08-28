"""Memory management utilities for Jarvis AI.

This module exposes various memory helpers. The real `ProjectMemory`
implementation depends on optional third‑party libraries. When those
dependencies are unavailable we provide a lightweight, file‑backed
fallback implementation so unit tests and basic environments can still
persist data.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from typing import Any, Dict, List, Optional

from .quantum_memory import QuantumMemory
from .replay_memory import Experience, ReplayMemory

# ---------------------------------------------------------------------------
# Optional import of the full-featured ProjectMemory
# ---------------------------------------------------------------------------
try:  # pragma: no cover - simple import guard
    from .project_memory import MemoryManager, ProjectMemory
except ImportError:  # pragma: no cover - used in minimal test environments

    class MemoryManager:  # type: ignore[no-redef]
        """File-backed project memory manager used as a fallback.

        Data is persisted as JSON lists under ``persist_directory``.
        Each project/session pair is stored in its own file. The format is
        intentionally simple to avoid external dependencies.
        """

        def __init__(
            self, persist_directory: str = "data/project_memory"
        ) -> None:
            self.persist_directory = persist_directory
            os.makedirs(self.persist_directory, exist_ok=True)
            self._lock = threading.Lock()

        # Internal helpers -------------------------------------------------
        def _path(self, project: str, session: str) -> str:
            filename = f"{project}_{session}.json"
            return os.path.join(self.persist_directory, filename)

        # Public API -------------------------------------------------------
        def add(
            self,
            project: str,
            session: str,
            text: str,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> str:
            """Store a text snippet and return its identifier.

            Raises:
                RuntimeError: If the memory cannot be written to disk.
            """

            record = {
                "id": str(uuid.uuid4()),
                "text": text,
                "metadata": metadata or {},
            }
            path = self._path(project, session)

            with self._lock:
                try:
                    data: List[Dict[str, Any]] = []
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                    data.append(record)
                    with open(path, "w", encoding="utf-8") as fh:
                        json.dump(data, fh)
                except (OSError, json.JSONDecodeError) as exc:
                    # pragma: no cover
                    raise RuntimeError(
                        f"Failed to add memory: {exc}"
                    ) from exc
            return record["id"]

        def query(
            self,
            project: str,
            session: str,
            text: Optional[str] = None,
            top_k: int = 5,
        ) -> List[Dict[str, Any]]:
            """Retrieve stored snippets matching ``text``.

            Args:
                project: Project identifier.
                session: Session identifier.
                text: Optional substring to search for. ``None`` returns all
                    entries.
                top_k: Maximum number of results to return.

            Raises:
                RuntimeError: If the backing store cannot be read.
            """

            path = self._path(project, session)
            with self._lock:
                try:
                    if not os.path.exists(path):
                        return []
                    with open(path, "r", encoding="utf-8") as fh:
                        data: List[Dict[str, Any]] = json.load(fh)
                except (OSError, json.JSONDecodeError) as exc:
                    # pragma: no cover
                    raise RuntimeError(
                        f"Failed to read memory: {exc}"
                    ) from exc

            if text:
                data = [d for d in data if text in d.get("text", "")]
            return data[:top_k]

        def update(
            self,
            project: str,
            session: str,
            record_id: str,
            text: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> None:
            """Update an existing memory entry.

            Raises:
                KeyError: If ``record_id`` is not found.
                RuntimeError: If the backing store cannot be written.
            """

            path = self._path(project, session)
            with self._lock:
                try:
                    if not os.path.exists(path):
                        raise KeyError(record_id)
                    with open(path, "r", encoding="utf-8") as fh:
                        data: List[Dict[str, Any]] = json.load(fh)
                    for item in data:
                        if item["id"] == record_id:
                            if text is not None:
                                item["text"] = text
                            if metadata is not None:
                                item["metadata"] = metadata
                            break
                    else:
                        raise KeyError(record_id)
                    with open(path, "w", encoding="utf-8") as fh:
                        json.dump(data, fh)
                except (OSError, json.JSONDecodeError) as exc:
                    # pragma: no cover
                    raise RuntimeError(
                        f"Failed to update memory: {exc}"
                    ) from exc

        def delete(
            self, project: str, session: str, record_id: str
        ) -> None:
            """Remove a memory entry.

            Raises:
                KeyError: If ``record_id`` is not found.
                RuntimeError: If the backing store cannot be written.
            """

            path = self._path(project, session)
            with self._lock:
                try:
                    if not os.path.exists(path):
                        raise KeyError(record_id)
                    with open(path, "r", encoding="utf-8") as fh:
                        data: List[Dict[str, Any]] = json.load(fh)
                    new_data = [d for d in data if d["id"] != record_id]
                    if len(new_data) == len(data):
                        raise KeyError(record_id)
                    if new_data:
                        with open(path, "w", encoding="utf-8") as fh:
                            json.dump(new_data, fh)
                    else:
                        os.remove(path)
                except (OSError, json.JSONDecodeError) as exc:
                    # pragma: no cover
                    raise RuntimeError(
                        f"Failed to delete memory: {exc}"
                    ) from exc

    class ProjectMemory(MemoryManager):  # type: ignore[no-redef]
        """Alias for the fallback MemoryManager."""

__all__ = [
    "Experience",
    "ReplayMemory",
    "MemoryManager",
    "ProjectMemory",
    "QuantumMemory",
]
