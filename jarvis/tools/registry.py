from __future__ import annotations

"""Tool registry v2 with JSON schema export and capability tagging."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Any, get_type_hints

from pydantic import BaseModel, create_model


@dataclass
class Tool:
    name: str
    func: Callable[..., Any]
    description: str
    capabilities: List[str]
    args_schema: type[BaseModel]

    def json_schema(self) -> Dict[str, Any]:
        return self.args_schema.schema()


class Registry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str,
        capabilities: List[str],
    ) -> None:
        annotations = get_type_hints(func)
        fields: Dict[str, tuple[Any, Any]] = {}
        for arg, annotation in annotations.items():
            if arg == "return":
                continue
            fields[arg] = (annotation, ...)
        schema = create_model(f"{name}_Args", **fields)  # type: ignore[arg-type]
        self._tools[name] = Tool(name, func, description, capabilities, schema)

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def all(self) -> Dict[str, Tool]:
        return dict(self._tools)

    def json_export(self) -> Dict[str, Any]:
        return {
            name: {
                "description": tool.description,
                "capabilities": tool.capabilities,
                "args_schema": tool.json_schema(),
            }
            for name, tool in self._tools.items()
        }


registry = Registry()
