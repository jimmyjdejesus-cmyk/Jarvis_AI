# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Protocol


class ExtensionHook(Protocol):
    def __call__(self, *args, **kwargs): ...


@dataclass
class ExtensionTemplate:
    """Defines a pluggable extension template such as MCP or LSP bridges."""

    name: str
    description: str
    entrypoint: Callable[..., object]
    config_schema: Dict[str, object]


MCP_TEMPLATE = ExtensionTemplate(
    name="mcp-adapter",
    description="Template for Model Context Protocol adapters.",
    entrypoint=lambda **kwargs: kwargs,
    config_schema={
        "server_uri": "wss://",
        "capabilities": ["tools", "memory"],
    },
)

LSP_TEMPLATE = ExtensionTemplate(
    name="lsp-bridge",
    description="Template for Language Server Protocol integrations.",
    entrypoint=lambda **kwargs: kwargs,
    config_schema={
        "language": "python",
        "command": "pylsp",
        "args": [],
    },
)

__all__ = ["ExtensionTemplate", "MCP_TEMPLATE", "LSP_TEMPLATE", "ExtensionHook"]
