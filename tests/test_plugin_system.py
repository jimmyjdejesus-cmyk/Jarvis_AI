"""Integration tests for plugin scaffolding."""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jarvis_sdk.registry import registry
from jarvis_sdk.scaffold import create_plugin


def test_scaffolded_plugin_executes(tmp_path):
    """A scaffolded plugin should register and echo input text."""
    registry._plugins.clear()
    create_plugin(tmp_path, "echo_plugin", description="Echo the text back")
    sys.path.insert(0, str(tmp_path))
    try:
        plugin_module = importlib.import_module("echo_plugin")
    finally:
        sys.path.pop(0)

    assert plugin_module.echo_plugin("hello") == "hello"
    assert "echo_plugin" in registry.all()
