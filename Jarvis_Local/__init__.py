"""Compatibility shim for legacy `Jarvis_Local` import path.

Importing `Jarvis_Local` will emit a DeprecationWarning and proxy to
`apps.AdaptiveMind_Local` so existing code continues to work.
"""
from __future__ import annotations

import importlib
import warnings

warnings.warn("`Jarvis_Local` moved to `apps.AdaptiveMind_Local`", DeprecationWarning, stacklevel=2)

_mod = importlib.import_module("apps.AdaptiveMind_Local")

# Re-export attributes from the real module so `import Jarvis_Local` behaves like before
for _name, _val in vars(_mod).items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _val

# Make this module a package proxy for pkgutil-style imports
__path__ = getattr(_mod, "__path__", [])
__all__ = getattr(_mod, "__all__", [])
