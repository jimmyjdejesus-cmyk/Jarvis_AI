# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, Protocol, Sequence


@dataclass
class GenerationRequest:
    messages: Sequence[dict]
    persona: str
    context: str
    temperature: float = 0.7
    max_tokens: int = 512
    metadata: Dict[str, str] | None = None


@dataclass
class GenerationResponse:
    content: str
    tokens: int
    backend: str
    diagnostics: Dict[str, str] | None = None


@dataclass
class GenerationChunk:
    content: str  # Incremental content (e.g., a token or partial text)
    tokens: int  # Cumulative tokens generated so far
    backend: str
    finished: bool  # True if this is the final chunk
    diagnostics: Dict[str, str] | None = None


class LLMBackend(Protocol):
    name: str

    def is_available(self) -> bool:
        ...

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        ...

    def stream(self, request: GenerationRequest) -> Iterator[GenerationChunk]:
        ...


__all__ = ["GenerationRequest", "GenerationResponse", "GenerationChunk", "LLMBackend"]
