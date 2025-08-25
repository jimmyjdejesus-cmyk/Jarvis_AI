"""Simple plugin registry and decorators for Jarvis SDK."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class PluginDescriptor:
    """Metadata about a registered plugin."""

    plugin: Any
    plugin_type: str
    description: str = ""
    permissions: List[str] = field(default_factory=list)


class PluginRegistry:
    """Holds registered plugins for discovery by Jarvis."""

    def __init__(self) -> None:  # pragma: no cover - trivial
        self._plugins: Dict[str, PluginDescriptor] = {}

    def register(
        self,
        item: Any,
        plugin_type: str,
        name: str | None = None,
        description: str = "",
        permissions: List[str] | None = None,
    ) -> Any:
        """Register a plugin object.

        Args:
            item: Callable or class implementing the plugin.
            plugin_type: Category of plugin (e.g., ``agent`` or ``tool``).
            name: Optional explicit name; defaults to object name.
            description: Optional human-readable description.
        """

        plugin_name = name or getattr(item, "__name__", item.__class__.__name__)
        self._plugins[plugin_name] = PluginDescriptor(
            item, plugin_type, description, permissions or []
        )
        return item

    def all(self) -> Dict[str, PluginDescriptor]:
        """Return a copy of all registered plugins."""
        return dict(self._plugins)


registry = PluginRegistry()


class AgentRegistry(PluginRegistry):
    """Registry dedicated to agent implementations."""


class ToolRegistry(PluginRegistry):
    """Registry dedicated to tool implementations."""


class CrewRegistry(PluginRegistry):
    """Registry dedicated to crew implementations."""


class CriticRegistry(PluginRegistry):
    """Registry dedicated to critic implementations."""


agent_registry = AgentRegistry()
tool_registry = ToolRegistry()
crew_registry = CrewRegistry()
critic_registry = CriticRegistry()


def jarvis_plugin(
    *,
    plugin_type: str,
    name: str | None = None,
    description: str = "",
    permissions: List[str] | None = None,
):
    """Generic decorator used by plugins to register themselves."""

    def decorator(func_or_cls: Callable) -> Callable:
        return registry.register(
            func_or_cls,
            plugin_type,
            name=name,
            description=description,
            permissions=permissions,
        )

    return decorator


def jarvis_agent(
    *, name: str | None = None, description: str = "", permissions: List[str] | None = None
):
    """Decorator for registering agent classes."""

    def decorator(cls: Callable) -> Callable:
        registry.register(
            cls, "agent", name=name, description=description, permissions=permissions
        )
        return agent_registry.register(
            cls, "agent", name=name, description=description, permissions=permissions
        )

    return decorator


def jarvis_tool(
    *, name: str | None = None, description: str = "", permissions: List[str] | None = None
):
    """Decorator for registering tool callables."""

    def decorator(func: Callable) -> Callable:
        registry.register(
            func, "tool", name=name, description=description, permissions=permissions
        )
        return tool_registry.register(
            func,
            "tool",
            name=name,
            description=description,
            permissions=permissions,
        )

    return decorator


def jarvis_crew(
    *, name: str | None = None, description: str = "", permissions: List[str] | None = None
):
    """Decorator for registering crew classes."""

    def decorator(cls: Callable) -> Callable:
        registry.register(
            cls, "crew", name=name, description=description, permissions=permissions
        )
        return crew_registry.register(
            cls, "crew", name=name, description=description, permissions=permissions
        )

    return decorator


def jarvis_critic(
    *, name: str | None = None, description: str = "", permissions: List[str] | None = None
):
    """Decorator for registering critic callables."""

    def decorator(func: Callable) -> Callable:
        registry.register(
            func, "critic", name=name, description=description, permissions=permissions
        )
        return critic_registry.register(
            func, "critic", name=name, description=description, permissions=permissions
        )

    return decorator
