"""Core agent container with extensible components."""
from __future__ import annotations

from typing import Any, Dict, Optional


class AgentCore:
    """Hold core agent dependencies and allow dynamic component attachment.

    Parameters
    ----------
    config:
        Optional configuration dictionary for the agent.
    event_bus:
        Optional event bus or message broker instance used by the agent.
    memory:
        Optional memory backend or service used by the agent.
    **components:
        Additional named components attached to the agent.
    """

    def __init__(
        self,
        config: Optional[dict] = None,
        event_bus: Any | None = None,
        memory: Any | None = None,
        **components: Any,
    ) -> None:
        self.config = config
        self.event_bus = event_bus
        self.memory = memory
        self.components: Dict[str, Any] = {}
        for name, component in components.items():
            self.add_component(name, component)

    def add_component(self, name: str, component: Any) -> None:
        """Attach a named component and expose it as an attribute."""
        self.components[name] = component
        setattr(self, name, component)

    def get_component(self, name: str) -> Any:
        """Retrieve a previously attached component by name.

        Raises
        ------
        KeyError
            If the component has not been attached to the agent.
        """
        try:
            return self.components[name]
        except KeyError as exc:
            raise KeyError(f"Component '{name}' is not attached") from exc

    def __repr__(self) -> str:
        extras = ", ".join(self.components)
        return (
            "AgentCore("  # pragma: no cover - simple representation helper
            f"config={self.config!r}, event_bus={self.event_bus!r}, "
            f"memory={self.memory!r}, components=[{extras}]"
            ")"
        )
