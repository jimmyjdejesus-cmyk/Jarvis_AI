from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol, Sequence


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


class LLMBackend(Protocol):
    name: str

    def is_available(self) -> bool:
        ...

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        ...


__all__ = ["GenerationRequest", "GenerationResponse", "LLMBackend"]
