"""Simple plugin registry and decorators for Jarvis SDK."""

from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass
class PluginInfo:
    """Metadata about a registered plugin."""
    plugin: Any
    plugin_type: str
    description: str = ""


class PluginRegistry:
    """Holds registered plugins for discovery by Jarvis."""

    def __init__(self) -> None:  # pragma: no cover - trivial
        self._plugins: Dict[str, PluginInfo] = {}

    def register(
        self,
        item: Any,
        plugin_type: str,
        name: str | None = None,
        description: str = "",
    ) -> Any:
        """Register a plugin object.

        Args:
            item: Callable or class implementing the plugin.
            plugin_type: Category of plugin (e.g., ``agent`` or ``tool``).
            name: Optional explicit name; defaults to object name.
            description: Optional human-readable description.
        """

        plugin_name = name or getattr(item, "__name__", item.__class__.__name__)
        self._plugins[plugin_name] = PluginInfo(item, plugin_type, description)
        return item

    def all(self) -> Dict[str, PluginInfo]:
        """Return a copy of all registered plugins."""
        return dict(self._plugins)


registry = PluginRegistry()


class AgentRegistry(PluginRegistry):
    """Registry dedicated to agent implementations."""


class ToolRegistry(PluginRegistry):
    """Registry dedicated to tool implementations."""


agent_registry = AgentRegistry()
tool_registry = ToolRegistry()


def jarvis_plugin(*, plugin_type: str, name: str | None = None, description: str = ""):
    """Generic decorator used by plugins to register themselves."""

    def decorator(func_or_cls: Callable) -> Callable:
        return registry.register(
            func_or_cls, plugin_type, name=name, description=description
        )

    return decorator


def jarvis_agent(*, name: str | None = None, description: str = ""):
    """Decorator for registering agent classes."""

    def decorator(cls: Callable) -> Callable:
        registry.register(cls, "agent", name=name, description=description)
        return agent_registry.register(
            cls, "agent", name=name, description=description
        )

    return decorator


def jarvis_tool(*, name: str | None = None, description: str = ""):
    """Decorator for registering tool callables."""

    def decorator(func: Callable) -> Callable:
        registry.register(func, "tool", name=name, description=description)
        return tool_registry.register(
            func, "tool", name=name, description=description
        )

    return decorator
