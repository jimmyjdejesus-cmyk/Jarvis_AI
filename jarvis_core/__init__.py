"""Compatibility shim for `jarvis_core` package name.

Re-exports the adaptivemind_core package so older imports like
`import jarvis_core.server` continue to work during the rebranding.
"""
from __future__ import annotations

# Re-export top-level names
from adaptivemind_core import *  # noqa: F401,F403

# Ensure submodules like `jarvis_core.server` are available for importers and
# tools that resolve attributes on the package (e.g., unittest.mock.patch).
try:
	from . import server  # type: ignore  # noqa: F401
except Exception:
	# If the server shim isn't available for any reason, ignore — tests will
	# import the real module via adaptivemind_core
	pass

__all__ = [name for name in globals().keys() if not name.startswith("_")]
