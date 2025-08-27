"""Memory management utilities for Jarvis AI."""


from __future__ import annotations

from .replay_memory import Experience, ReplayMemory

# The full ProjectMemory implementation pulls in optional dependencies. For
# testing (and to avoid import errors when those dependencies are missing) we
# attempt to import the real implementation but fall back to lightweight stubs.
try:  # pragma: no cover - simple import guard
    from .project_memory import MemoryManager, ProjectMemory
except Exception:  # pragma: no cover - used in minimal test environments
    class MemoryManager:  # type: ignore[misc]
        def add(self, *args, **kwargs):  # pragma: no cover - stub
            raise NotImplementedError

        def query(self, *args, **kwargs):  # pragma: no cover - stub
            raise NotImplementedError

    class ProjectMemory(MemoryManager):  # type: ignore[misc]
        pass

# Importing project memory can fail in minimal environments where optional
# dependencies like Chroma are unavailable. Perform the import lazily so that
# basic utilities (e.g. MemoryClient) remain usable.
try:  # pragma: no cover - optional import
    from .project_memory import MemoryManager, ProjectMemory  # type: ignore

    __all__ = ["Experience", "ReplayMemory", "MemoryManager", "ProjectMemory"]
except Exception:  # pragma: no cover - import guard
    __all__: list[str] = ["Experience", "ReplayMemory"]
