# jarvis/memory log
- Added `push` helper to `ReplayMemory` for compatibility with existing tests.
- Standardized log messages for push and recall operations.
# Agent Log
- Implemented file-backed fallback MemoryManager and ProjectMemory in __init__.py.
- Added update/delete operations and thread-safe file access.
- Extended fallback memory with fcntl locking for multi-process safety.