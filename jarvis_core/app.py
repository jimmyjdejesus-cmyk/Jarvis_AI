from __future__ import annotations

import threading
from dataclasses import asdict
from typing import Iterable, List, Optional

from .config import AppConfig, load_config
from .context.engine import ContextEngine
from .llm.fallback import ContextualFallbackLLM
from .llm.ollama import OllamaBackend
from .llm.windowsml import WindowsMLBackend
from .logging import get_logger
from .monitoring.metrics import MetricsRegistry, TraceCollector
from .routing.router import AdaptiveLLMRouter

logger = get_logger(__name__)


class JarvisApplication:
    """Coordinator that wires configuration, routing, and monitoring."""

    def __init__(self, config: Optional[AppConfig] = None):
        import time
        self._start_time = time.time()
        self.config = config or load_config()
        self.metrics = MetricsRegistry()
        self.traces = TraceCollector()
        self.context_engine = ContextEngine(self.config)
        self.backends = self._build_backends()
        self.router = AdaptiveLLMRouter(
            config=self.config,
            context_engine=self.context_engine,
            backends=self.backends,
            metrics=self.metrics,
            traces=self.traces,
        )
        self._harvester_thread: Optional[threading.Thread] = None
        self._stop_harvest = threading.Event()
        if self.config.monitoring.enable_metrics_harvest:
            self._start_harvest_loop()

    def _build_backends(self):
        backends = [
            OllamaBackend(
                host=self.config.ollama.host,
                model=self.config.ollama.model,
                timeout=self.config.ollama.timeout,
            ),
            WindowsMLBackend(
                model_path=self.config.windowsml.model_path,
                device_preference=self.config.windowsml.device_preference,
            ),
            ContextualFallbackLLM(),
        ]
        return backends

    def _start_harvest_loop(self) -> None:
        interval = self.config.monitoring.harvest_interval_s
        logger.info("Starting metrics harvest loop", extra={"interval": interval})

        def _loop():
            while not self._stop_harvest.wait(interval):
                snapshot = self.metrics.harvest()
                logger.info(
                    "Metrics harvested",
                    extra={
                        "requests": snapshot.request_count,
                        "avg_latency_ms": round(snapshot.average_latency_ms, 2),
                        "max_latency_ms": round(snapshot.max_latency_ms, 2),
                        "tokens": snapshot.tokens_generated,
                        "context_tokens": snapshot.context_tokens,
                        "personas": snapshot.personas_used,
                    },
                )

        self._harvester_thread = threading.Thread(target=_loop, name="metrics-harvester", daemon=True)
        self._harvester_thread.start()

    def shutdown(self) -> None:
        if self._harvester_thread and self._harvester_thread.is_alive():
            self._stop_harvest.set()
            self._harvester_thread.join(timeout=2)

    # API operations -----------------------------------------------------

    def chat(
        self,
        persona: str,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 512,
        metadata: Optional[dict] = None,
        external_context: Iterable[str] | None = None,
    ):
        response = self.router.generate(
            persona_name=persona,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata=metadata,
            external_context=external_context,
        )
        return {
            "content": response.content,
            "model": response.backend,
            "tokens": response.tokens,
            "diagnostics": response.diagnostics or {},
        }

    def personas(self) -> List[dict]:
        return [
            {
                "name": persona.name,
                "description": persona.description,
                "max_context_window": persona.max_context_window,
                "routing_hint": persona.routing_hint,
            }
            for persona in self.config.personas.values()
        ]

    def models(self) -> List[str]:
        return [backend.name for backend in self.backends if backend.is_available()]

    def traces_latest(self, limit: int = 50):
        return [asdict(trace) for trace in self.traces.latest(limit)]

    def metrics_snapshot(self):
        return [asdict(snapshot) for snapshot in self.metrics.history()]

    # Management API methods ---------------------------------------------

    def system_status(self) -> dict:
        """Get overall system status."""
        import time
        import hashlib

        # Calculate config hash for change detection
        config_str = str(self.config.model_dump())
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]

        return {
            "status": "healthy",  # TODO: implement proper health check
            "uptime_seconds": time.time() - self._start_time,
            "version": "1.0.0",
            "active_backends": [b.name for b in self.backends if b.is_available()],
            "active_personas": list(self.config.allowed_personas),
            "config_hash": config_hash,
        }

    def get_routing_config(self) -> dict:
        """Get current routing configuration."""
        return {
            "allowed_personas": list(self.config.allowed_personas),
            "enable_adaptive_routing": True,  # TODO: make configurable
        }

    def list_backends(self) -> List[dict]:
        """List all backends with their status."""
        import time
        backends = []
        for backend in self.backends:
            backends.append({
                "name": backend.name,
                "type": backend.__class__.__name__.lower().replace('backend', ''),
                "is_available": backend.is_available(),
                "last_checked": time.time(),  # TODO: track actual last check time
                "config": {},  # TODO: expose relevant config without secrets
            })
        return backends

    def get_context_config(self) -> dict:
        """Get current context pipeline configuration."""
        return {
            "extra_documents_dir": str(self.config.context_pipeline.extra_documents_dir) if self.config.context_pipeline.extra_documents_dir else None,
            "enable_semantic_chunking": self.config.context_pipeline.enable_semantic_chunking,
            "max_combined_context_tokens": self.config.context_pipeline.max_combined_context_tokens,
        }

    def get_security_status(self) -> dict:
        """Get security configuration status."""
        return {
            "api_keys_count": len(self.config.security.api_keys),
            "audit_log_enabled": self.config.security.audit_log_path is not None,
        }


__all__ = ["JarvisApplication"]
