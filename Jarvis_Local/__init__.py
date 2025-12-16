"""Compatibility shim for the moved `Jarvis_Local` package.

This module re-exports the real package under `apps.Jarvis_Local`
and emits a DeprecationWarning so older code still importing
`Jarvis_Local` continues to work.
"""
from __future__ import annotations

import importlib
import warnings
from types import ModuleType

warnings.warn("`Jarvis_Local` moved to `apps.Jarvis_Local` - import that package instead",
              DeprecationWarning, stacklevel=2)

_mod = importlib.import_module("apps.Jarvis_Local")

# Re-export attributes from the real module so `import Jarvis_Local` behaves like before
for _name, _val in vars(_mod).items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _val

# Make this module a package proxy for pkgutil-style imports
__path__ = getattr(_mod, "__path__", [])
__all__ = getattr(_mod, "__all__", [])
