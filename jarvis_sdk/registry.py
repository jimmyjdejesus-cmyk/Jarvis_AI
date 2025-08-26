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


def _validate_permissions(permissions: List[str] | None) -> List[str]:
    """Ensure permissions is a list of strings."""
    if permissions is None:
        return []
    if not isinstance(permissions, list) or not all(isinstance(p, str) for p in permissions):
        raise ValueError("permissions must be a list of strings")
    return permissions


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
            item, plugin_type, description, _validate_permissions(permissions)
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


def _decorator_factory(plugin_type: str, target: PluginRegistry) -> Callable:
    """Return a decorator registering to both global and target registries."""

    def decorator(
        *, name: str | None = None, description: str = "", permissions: List[str] | None = None
    ) -> Callable:
        def wrapper(obj: Callable) -> Callable:
            registry.register(
                obj,
                plugin_type,
                name=name,
                description=description,
                permissions=permissions,
            )
            return target.register(
                obj,
                plugin_type,
                name=name,
                description=description,
                permissions=permissions,
            )

        return wrapper

    return decorator


jarvis_agent = _decorator_factory("agent", agent_registry)
jarvis_tool = _decorator_factory("tool", tool_registry)
jarvis_crew = _decorator_factory("crew", crew_registry)
jarvis_critic = _decorator_factory("critic", critic_registry)