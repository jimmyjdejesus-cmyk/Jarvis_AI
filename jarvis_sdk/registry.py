"""Simple plugin registry and decorator."""
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

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginInfo] = {}

    def register(
        self,
        item: Any,
        plugin_type: str,
        name: str | None = None,
        description: str = "",
    ) -> Any:
        plugin_name = name or getattr(item, "__name__", item.__class__.__name__)
        self._plugins[plugin_name] = PluginInfo(item, plugin_type, description)
        return item

    def all(self) -> Dict[str, PluginInfo]:
        return dict(self._plugins)


registry = PluginRegistry()


def jarvis_plugin(*, plugin_type: str, name: str | None = None, description: str = ""):
    """Decorator used by plugins to register themselves."""

    def decorator(func_or_cls: Callable) -> Callable:
        return registry.register(func_or_cls, plugin_type, name=name, description=description)

    return decorator
