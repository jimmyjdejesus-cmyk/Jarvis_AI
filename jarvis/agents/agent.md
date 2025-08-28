# Agent Log - jarvis/agents

- Added `curiosity_router.py` to enqueue curiosity questions as mission directives.
- Updated package exports to expose `CuriosityRouter`.
# Agent Log
- Hardened specialist discovery against optional dependency errors and added code review specialist.
## Dev Log
- Created CuriosityRouter to convert curiosity questions into mission directives.
- [2025-08-27T20:19:27+00:00] Hardened CuriosityRouter input sanitization.

## Agent Log 2025-09-07
- Implemented PersistentQueue with Redis fallback and logging.
- Updated CuriosityRouter to use persistent queue and sanitize directives.
