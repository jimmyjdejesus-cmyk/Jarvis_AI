"""Integration tests for plugin scaffolding and discovery."""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jarvis_sdk.registry import (
    registry,
    agent_registry,
    crew_registry,
    critic_registry,
    tool_registry,
)
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


def test_manifest_discovery_registers_plugins() -> None:
    """Importing ``jarvis.plugins`` should register manifest-listed plugins."""
    for reg in (registry, agent_registry, crew_registry, critic_registry, tool_registry):
        reg._plugins.clear()

    for mod in [m for m in list(sys.modules) if m.startswith("jarvis.plugins")]:
        del sys.modules[mod]

    import jarvis.plugins as plugins
    importlib.reload(plugins)

    assert "greet" in registry.all()
    assert registry.all()["greet"].plugin_type == "tool"
    assert registry.all()["MathSpecialist"].plugin_type == "specialist"
    assert "EchoCrew" in crew_registry.all()
    assert "length_checker" in critic_registry.all()
