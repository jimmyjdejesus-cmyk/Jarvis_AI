"""Memory management utilities for Jarvis AI."""

# The full ProjectMemory implementation pulls in optional dependencies.  For
# testing (and to avoid import errors when those dependencies are missing) we
# attempt to import the real implementation but fall back to lightweight
# stubs.
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

__all__ = ["MemoryManager", "ProjectMemory"]
