# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

import time
import uuid
from typing import Dict, Iterable, Iterator, Sequence

from ..config import AppConfig, PersonaConfig
from ..logger import get_logger
from ..monitoring.metrics import MetricsRegistry, TraceCollector, TraceRecord
from ..context.engine import ContextEngine
from ..llm.base import GenerationChunk, GenerationRequest, GenerationResponse, LLMBackend

logger = get_logger(__name__)


class AdaptiveLLMRouter:
    """Selects the best backend based on persona hints and availability."""

    def __init__(
        self,
        config: AppConfig,
        context_engine: ContextEngine,
        backends: Sequence[LLMBackend],
        metrics: MetricsRegistry,
        traces: TraceCollector,
    ):
        self._config = config
        self._context_engine = context_engine
        self._backends = list(backends)
        self._metrics = metrics
        self._traces = traces

    def available_personas(self) -> Dict[str, PersonaConfig]:
        return self._config.personas

    def select_backend(self, persona: PersonaConfig) -> LLMBackend:
        for backend in self._backends:
            if backend.is_available():
                logger.debug("Selected backend", extra={"persona": persona.name, "backend": backend.name})
                return backend
        logger.warning("Falling back to contextual generator", extra={"persona": persona.name})
        return self._backends[-1]

    def generate(
        self,
        persona_name: str,
        messages: Sequence[dict],
        temperature: float = 0.7,
        max_tokens: int = 512,
        metadata: Dict[str, str] | None = None,
        external_context: Iterable[str] | None = None,
    ) -> GenerationResponse:
        if persona_name not in self._config.allowed_personas:
            raise ValueError(f"Persona '{persona_name}' is not enabled")
        persona = self._config.personas[persona_name]
        context = self._context_engine.build_context(persona, messages, external_context)
        backend = self.select_backend(persona)
        request = GenerationRequest(
            messages=messages,
            persona=persona.name,
            context=context,
            temperature=temperature,
            max_tokens=min(max_tokens, persona.max_context_window),
            metadata=metadata,
        )
        start = time.perf_counter()
        response = backend.generate(request)
        latency_ms = (time.perf_counter() - start) * 1000
        context_tokens = len(context.split())
        self._metrics.record_request(persona=persona.name, latency_ms=latency_ms, generated_tokens=response.tokens, context_tokens=context_tokens)
        trace = TraceRecord(
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            persona=persona.name,
            objective=metadata.get("objective") if metadata else "chat",
            latency_ms=latency_ms,
            token_usage=response.tokens,
            context_size=context_tokens,
            backend=response.backend,
        )
        self._traces.add(trace)
        logger.info(
            "Generation completed",
            extra={
                "persona": persona.name,
                "backend": response.backend,
                "latency_ms": round(latency_ms, 2),
                "tokens": response.tokens,
                "context_tokens": context_tokens,
            },
        )
        return response

    def stream(
        self,
        persona_name: str,
        messages: Sequence[dict],
        temperature: float = 0.7,
        max_tokens: int = 512,
        metadata: Dict[str, str] | None = None,
        external_context: Iterable[str] | None = None,
    ) -> Iterator[GenerationChunk]:
        if persona_name not in self._config.allowed_personas:
            raise ValueError(f"Persona '{persona_name}' is not enabled")
        persona = self._config.personas[persona_name]
        context = self._context_engine.build_context(persona, messages, external_context)
        backend = self.select_backend(persona)
        request = GenerationRequest(
            messages=messages,
            persona=persona.name,
            context=context,
            temperature=temperature,
            max_tokens=min(max_tokens, persona.max_context_window),
            metadata=metadata,
        )
        start = time.perf_counter()
        chunk_count = 0
        for chunk in backend.stream(request):
            chunk_count += 1
            yield chunk
            if chunk.finished:
                latency_ms = (time.perf_counter() - start) * 1000
                context_tokens = len(context.split())
                self._metrics.record_request(persona=persona.name, latency_ms=latency_ms, generated_tokens=chunk.tokens, context_tokens=context_tokens)
                trace = TraceRecord(
                    trace_id=str(uuid.uuid4()),
                    span_id=str(uuid.uuid4()),
                    persona=persona.name,
                    objective=metadata.get("objective") if metadata else "chat",
                    latency_ms=latency_ms,
                    token_usage=chunk.tokens,
                    context_size=context_tokens,
                    backend=chunk.backend,
                )
                self._traces.add(trace)
                logger.info(
                    "Streaming generation completed",
                    extra={
                        "persona": persona.name,
                        "backend": chunk.backend,
                        "latency_ms": round(latency_ms, 2),
                        "tokens": chunk.tokens,
                        "context_tokens": context_tokens,
                        "chunks": chunk_count,
                    },
                )
                break


__all__ = ["AdaptiveLLMRouter"]
