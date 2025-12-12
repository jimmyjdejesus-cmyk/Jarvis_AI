"""Minimal config loader shim used by legacy code during tests.

This returns an empty dict for missing configuration. It's safe for tests
and small enough to avoid importing heavy config packages.
"""

from typing import Any, Dict, Optional


def load_config(explicit_path: Optional[str] = None) -> Dict[str, Any]:
    return {}
