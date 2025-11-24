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

    # Phase 2: Mutation methods ---------------------------------------------

    def create_persona(self, persona_data: dict) -> dict:
        """Create a new persona."""
        name = persona_data["name"]
        if name in self.config.personas:
            raise ValueError(f"Persona '{name}' already exists")

        from .config import PersonaConfig
        persona_config = PersonaConfig(**persona_data)
        self.config.personas[name] = persona_config

        # Add to allowed personas if not already there
        if name not in self.config.allowed_personas:
            self.config.allowed_personas.append(name)

        return self._persona_to_dict(name, persona_config)

    def update_persona(self, name: str, updates: dict) -> dict:
        """Update an existing persona."""
        if name not in self.config.personas:
            raise ValueError(f"Persona '{name}' not found")

        persona = self.config.personas[name]
        for key, value in updates.items():
            if value is not None:
                setattr(persona, key, value)

        return self._persona_to_dict(name, persona)

    def delete_persona(self, name: str) -> bool:
        """Delete a persona."""
        if name not in self.config.personas:
            raise ValueError(f"Persona '{name}' not found")

        # Prevent deletion of personas that might be in use
        # For now, allow deletion but log warning
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Deleting persona '{name}'")

        del self.config.personas[name]

        # Remove from allowed personas
        if name in self.config.allowed_personas:
            self.config.allowed_personas.remove(name)

        return True

    def update_routing_config(self, updates: dict) -> dict:
        """Update routing configuration."""
        if "allowed_personas" in updates and updates["allowed_personas"] is not None:
            # Validate that all personas exist
            for persona_name in updates["allowed_personas"]:
                if persona_name not in self.config.personas:
                    raise ValueError(f"Persona '{persona_name}' does not exist")
            self.config.allowed_personas = updates["allowed_personas"]

        if "enable_adaptive_routing" in updates and updates["enable_adaptive_routing"] is not None:
            # For now, this is a placeholder - adaptive routing is always enabled
            pass

        return self.get_routing_config()

    def update_context_config(self, updates: dict) -> dict:
        """Update context pipeline configuration."""
        context_config = self.config.context_pipeline

        if "extra_documents_dir" in updates and updates["extra_documents_dir"] is not None:
            from pathlib import Path
            context_config.extra_documents_dir = Path(updates["extra_documents_dir"])

        if "enable_semantic_chunking" in updates and updates["enable_semantic_chunking"] is not None:
            context_config.enable_semantic_chunking = updates["enable_semantic_chunking"]

        if "max_combined_context_tokens" in updates and updates["max_combined_context_tokens"] is not None:
            context_config.max_combined_context_tokens = updates["max_combined_context_tokens"]

        return self.get_context_config()

    def test_backend(self, name: str) -> dict:
        """Test backend connectivity."""
        import time
        backend = None
        for b in self.backends:
            if b.name == name:
                backend = b
                break

        if not backend:
            raise ValueError(f"Backend '{name}' not found")

        start_time = time.time()
        try:
            # Simple test - check if backend is available
            is_available = backend.is_available()
            latency = (time.time() - start_time) * 1000
            return {
                "success": is_available,
                "latency_ms": latency,
                "error": None
            }
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return {
                "success": False,
                "latency_ms": latency,
                "error": str(e)
            }

    def save_config(self) -> dict:
        """Save current configuration to disk."""
        try:
            # For now, this is a placeholder - config persistence would require
            # writing to the config file, which is complex in a running system
            import hashlib
            config_str = str(self.config.model_dump())
            config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]

            return {
                "success": True,
                "config_hash": config_hash,
                "message": "Configuration saved successfully (in-memory only for now)"
            }
        except Exception as e:
            return {
                "success": False,
                "config_hash": "",
                "message": f"Failed to save configuration: {str(e)}"
            }

    def _persona_to_dict(self, name: str, persona) -> dict:
        """Convert persona config to dict response."""
        return {
            "name": name,
            "description": persona.description,
            "system_prompt": persona.system_prompt,
            "max_context_window": persona.max_context_window,
            "routing_hint": persona.routing_hint,
            "is_active": name in self.config.allowed_personas
        }


__all__ = ["JarvisApplication"]
