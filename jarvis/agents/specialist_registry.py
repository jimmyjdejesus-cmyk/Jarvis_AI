"""Factory and registry for specialist agents."""
from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from typing import Any, Dict, Type

from .specialist import SpecialistAgent

_SPECIALIST_REGISTRY: Dict[str, Type[SpecialistAgent]] = {}


def _discover_specialists() -> None:
    """Dynamically discover and register specialists."""
    if _SPECIALIST_REGISTRY:
        return

    import jarvis.agents as agents_package

    def is_specialist_class(member: Any) -> bool:
        return (
            inspect.isclass(member)
            and issubclass(member, SpecialistAgent)
            and member is not SpecialistAgent
        )

    for _, name, _ in pkgutil.walk_packages(
        agents_package.__path__,
        agents_package.__name__ + ".",
        onerror=lambda _: None,
    ):
        try:
            module = importlib.import_module(name)
        except Exception:  # pragma: no cover - skip optional deps
            logging.debug(
                "Skipping specialist module %s due to import error", name
            )
            continue

        for _, cls in inspect.getmembers(module, is_specialist_class):
            # Use a more descriptive name for registration
            specialist_name = (
                cls.__name__
                .lower()
                .replace("specialist", "")
                .replace("agent", "")
            )
            _SPECIALIST_REGISTRY[specialist_name] = cls


def get_specialist_registry() -> Dict[str, Type[SpecialistAgent]]:
    """Return the specialist registry, discovering specialists if necessary."""
    _discover_specialists()
    return _SPECIALIST_REGISTRY


def create_specialist(name: str, mcp_client: Any, **kwargs) -> SpecialistAgent:
    """Instantiate a specialist by name."""
    registry = get_specialist_registry()
    cls = registry.get(name)
    if cls is None:
        raise KeyError(f"Unknown specialist: {name}")
    return cls(mcp_client=mcp_client, **kwargs)
