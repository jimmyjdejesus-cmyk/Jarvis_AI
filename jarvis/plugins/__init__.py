"""Plugin auto-discovery for Jarvis.

Modules listed in `manifest.json` are imported at package import time,
allowing them to register with :mod:`jarvis_sdk` automatically.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

MANIFEST = Path(__file__).with_name("manifest.json")


def discover_plugins() -> None:
    """Import all plugins specified in the manifest."""
    if not MANIFEST.exists():
        return
    data = json.loads(MANIFEST.read_text())
    for module in data.get("plugins", []):
        importlib.import_module(f"{__name__}.{module}")


# Discover plugins on import
discover_plugins()
