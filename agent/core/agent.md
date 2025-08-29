# agent/core activity log

- Added `core.py` with `JarvisAgent` implementation using replay memory.
- Updated `__init__.py` to expose `JarvisAgent` for imports.
- Adapted planning logic for `ReplayMemory` `Experience` records.
# Agent Log
- Implemented minimal `AgentCore` class capturing configuration, event bus, and memory references.
- Ensured package `__init__` re-exports `AgentCore` and added placeholder `run` method.
- Added component registry, add/get helpers, and repr for AgentCore.

- Updated `get_component` to raise KeyError on missing components and extended tests accordingly.