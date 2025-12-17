# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""Main Jarvis Application module providing the core coordinator for AI operations.

This module contains the JarvisApplication class which serves as the main coordinator
that wires together configuration, routing, monitoring, and all backend services.
It provides the high-level API for chat operations, persona management, and system
monitoring.
"""

from __future__ import annotations

import threading
import time
from dataclasses import asdict
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

from .config import AppConfig, load_config
from .context.engine import ContextEngine
from .llm.fallback import ContextualFallbackLLM
from .llm.ollama import OllamaBackend
from .llm.openrouter import OpenRouterBackend
from .llm.windowsml import WindowsMLBackend
from .logger import get_logger
from .monitoring.metrics import MetricsRegistry, TraceCollector
from .routing.router import AdaptiveLLMRouter

logger = get_logger(__name__)


class JarvisApplication:
    """Main coordinator that wires configuration, routing, and monitoring.
    
    The JarvisApplication class serves as the central coordinator for all Jarvis
    operations. It initializes and manages:
    - Configuration management via AppConfig
    - Multiple LLM backends (Ollama, OpenRouter, WindowsML, Fallback)
    - Adaptive routing for optimal backend selection
    - Context processing and semantic chunking
    - Metrics collection and tracing
    - Background harvesting of performance metrics
    
    This class provides the primary API for:
    - Chat operations (both sync and streaming)
    - Persona management (create, update, delete)
    - System monitoring and health checks
    - Backend testing and status
    - Configuration management
    
    Attributes:
        config: Application configuration containing all settings
        metrics: Registry for collecting and tracking performance metrics
        traces: Collector for request tracing and diagnostics
        context_engine: Engine for processing and managing context
        backends: List of configured LLM backends
        router: Adaptive router for backend selection
        _harvester_thread: Background thread for metrics harvesting
        _stop_harvest: Event to signal harvester thread to stop
        _start_time: Application startup timestamp
    """

    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize the Jarvis application with all components.
        
        Args:
            config: Optional AppConfig instance. If None, loads default config
                   from standard locations (env vars, config files, etc.)
        """
        self._start_time = time.time()
        self.config = config or load_config()
        
        # Initialize core components
        self.metrics = MetricsRegistry()
        self.traces = TraceCollector()
        self.context_engine = ContextEngine(self.config)
        
        # Build and configure backend services
        self.backends = self._build_backends()
        self.router = AdaptiveLLMRouter(
            config=self.config,
            context_engine=self.context_engine,
            backends=self.backends,
            metrics=self.metrics,
            traces=self.traces,
        )
        
        # Initialize background metrics harvesting
        self._harvester_thread: Optional[threading.Thread] = None
        self._stop_harvest = threading.Event()
        
        # Start metrics harvesting if enabled in configuration
        if self.config.monitoring.enable_metrics_harvest:
            self._start_harvest_loop()

    def _build_backends(self) -> List:
        """Build and configure all available LLM backends.
        
        Creates instances of all configured backends:
        - OllamaBackend for local model hosting
        - OpenRouterBackend for cloud-based models
        - WindowsMLBackend for local ONNX models
        - ContextualFallbackLLM for fallback operations
        
        Returns:
            List of configured backend instances
        """
        backends = [
            OllamaBackend(
                host=self.config.ollama.host,
                model=self.config.ollama.model,
                timeout=self.config.ollama.timeout,
            ),
            OpenRouterBackend(
                api_key=self.config.openrouter.api_key,
                model=self.config.openrouter.model,
                site_url=self.config.openrouter.site_url,
                app_name=self.config.openrouter.app_name,
            ),
            WindowsMLBackend(
                model_path=self.config.windowsml.model_path,
                device_preference=self.config.windowsml.device_preference,
            ),
            ContextualFallbackLLM(),
        ]
        return backends

    def _start_harvest_loop(self) -> None:
        """Start the background metrics harvesting loop.
        
        Runs a daemon thread that periodically harvests and logs metrics
        at the configured interval. The loop continues until the stop
        event is set or the application shuts down.
        """
        interval = self.config.monitoring.harvest_interval_s
        logger.info("Starting metrics harvest loop", extra={"interval": interval})

        def _loop():
            """Inner loop function for metrics harvesting."""
            while not self._stop_harvest.wait(interval):
                # Collect metrics snapshot
                snapshot = self.metrics.harvest()
                
                # Log detailed metrics for monitoring
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

        # Start the harvester thread with a descriptive name
        self._harvester_thread = threading.Thread(target=_loop, name="metrics-harvester", daemon=True)
        self._harvester_thread.start()

    def shutdown(self) -> None:
        """Gracefully shutdown the Jarvis application.
        
        Stops the metrics harvesting loop and waits for the harvester
        thread to finish. Called automatically during application cleanup.
        """
        if self._harvester_thread and self._harvester_thread.is_alive():
            self._stop_harvest.set()
            self._harvester_thread.join(timeout=2)

    # API operations -----------------------------------------------------

    def chat(
        self,
        persona: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        metadata: Optional[Dict[str, Any]] = None,
        external_context: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a chat response using the specified persona.
        
        Routes the chat request to the appropriate backend based on the persona
        configuration and current system load. Processes messages through the
        context pipeline and returns structured response data.
        
        Args:
            persona: Name of the persona to use for generation
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness in generation (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            metadata: Optional metadata to include with the request
            external_context: Optional iterable of external context strings
            
        Returns:
            Dict containing:
            - content: Generated response text
            - model: Backend model used for generation
            - tokens: Number of tokens generated
            - diagnostics: Backend-specific diagnostic information
        """
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

    def stream_chat(
        self,
        persona: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        metadata: Optional[Dict[str, Any]] = None,
        external_context: Optional[Iterable[str]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Stream a chat response incrementally.
        
        Similar to chat() but yields response chunks as they become available,
        enabling real-time streaming responses for better user experience.
        
        Args:
            persona: Name of the persona to use for generation
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness in generation (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            metadata: Optional metadata to include with the request
            external_context: Optional iterable of external context strings
            
        Yields:
            Dict chunks containing:
            - content: Incremental response text
            - model: Backend model used for generation
            - tokens: Total tokens generated so far
            - finished: Whether generation is complete
            - diagnostics: Backend-specific diagnostic information
        """
        for chunk in self.router.stream(
            persona_name=persona,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata=metadata,
            external_context=external_context,
        ):
            yield {
                "content": chunk.content,
                "model": chunk.backend,
                "tokens": chunk.tokens,
                "finished": chunk.finished,
                "diagnostics": chunk.diagnostics or {},
            }

    def personas(self) -> List[Dict[str, Any]]:
        """Get all configured personas.
        
        Returns a list of all personas currently configured in the system,
        including their descriptions and operational parameters.
        
        Returns:
            List of persona dictionaries containing name, description,
            max_context_window, and routing_hint
        """
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
        """Get list of available model backends.
        
        Returns the names of all LLM backends that are currently available
        and operational.
        
        Returns:
            List of available backend model names
        """
        return [backend.name for backend in self.backends if backend.is_available()]

    def traces_latest(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the latest request traces for debugging.
        
        Retrieves recent request traces showing the routing decisions,
        timing, and diagnostic information for troubleshooting.
        
        Args:
            limit: Maximum number of traces to return
            
        Returns:
            List of trace dictionaries with request details and timing
        """
        return [asdict(trace) for trace in self.traces.latest(limit)]

    def metrics_snapshot(self) -> List[Dict[str, Any]]:
        """Get current metrics snapshot.
        
        Returns performance metrics collected since the last harvest,
        including request counts, latency statistics, and token usage.
        
        Returns:
            List of metrics snapshots with performance data
        """
        return [asdict(snapshot) for snapshot in self.metrics.history()]

    # Management API methods ---------------------------------------------

    def system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and health information.
        
        Returns detailed information about the current system state including
        uptime, active components, configuration hash for change detection,
        and overall health status.
        
        Returns:
            Dict containing:
            - status: Overall system health ("healthy", "degraded", "unhealthy")
            - uptime_seconds: Time since application startup
            - version: Application version string
            - active_backends: List of available backend names
            - active_personas: List of currently allowed personas
            - config_hash: Hash of current configuration for change detection
        """
        import time
        import hashlib

        # Calculate config hash for change detection
        config_str = self.config.model_dump_json()
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]

        return {
            "status": "healthy",  # TODO: implement proper health check
            "uptime_seconds": time.time() - self._start_time,
            "version": "1.0.0",
            "active_backends": [b.name for b in self.backends if b.is_available()],
            "active_personas": list(self.config.allowed_personas),
            "config_hash": config_hash,
        }

    def get_routing_config(self) -> Dict[str, Any]:
        """Get current routing and persona configuration.
        
        Returns the current routing settings including which personas are
        allowed and whether adaptive routing is enabled.
        
        Returns:
            Dict containing:
            - allowed_personas: List of personas that can be used for routing
            - enable_adaptive_routing: Whether adaptive routing is enabled
        """
        return {
            "allowed_personas": list(self.config.allowed_personas),
            "enable_adaptive_routing": True,  # TODO: make configurable
        }

    def list_backends(self) -> List[Dict[str, Any]]:
        """Get status information for all configured backends.
        
        Returns detailed status for each configured backend including
        availability, type, and configuration summary.
        
        Returns:
            List of backend status dicts containing:
            - name: Backend name identifier
            - type: Backend type (ollama, openrouter, windowsml, fallback)
            - is_available: Whether backend is currently operational
            - last_checked: Timestamp of last availability check
            - config: Backend configuration summary (secrets excluded)
        """
        import time
        backends = [
            {
                "name": backend.name,
                "type": backend.__class__.__name__.lower().replace('backend', ''),
                "is_available": backend.is_available(),
                "last_checked": time.time(),  # TODO: track actual last check time
                "config": {},  # TODO: expose relevant config without secrets
            }
            for backend in self.backends
        ]
        return backends

    def get_context_config(self) -> Dict[str, Any]:
        """Get current context pipeline configuration.
        
        Returns the configuration for the context processing pipeline,
        including document loading, semantic chunking, and token limits.
        
        Returns:
            Dict containing:
            - extra_documents_dir: Optional directory for additional documents
            - enable_semantic_chunking: Whether semantic chunking is enabled
            - max_combined_context_tokens: Maximum tokens for combined context
        """
        return {
            "extra_documents_dir": str(self.config.context_pipeline.extra_documents_dir) if self.config.context_pipeline.extra_documents_dir else None,
            "enable_semantic_chunking": self.config.context_pipeline.enable_semantic_chunking,
            "max_combined_context_tokens": self.config.context_pipeline.max_combined_context_tokens,
        }

    def get_security_status(self) -> Dict[str, Any]:
        """Get security configuration and status information.
        
        Returns information about the security configuration including
        API key management and audit logging status.
        
        Returns:
            Dict containing:
            - api_keys_count: Number of configured API keys
            - audit_log_enabled: Whether audit logging is enabled
        """
        return {
            "api_keys_count": len(self.config.security.api_keys),
            "audit_log_enabled": self.config.security.audit_log_path is not None,
        }

    # Phase 2: Mutation methods ---------------------------------------------

    def create_persona(self, persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new persona configuration.
        
        Creates a new persona with the provided configuration data and
        adds it to the allowed personas list. Validates that the persona
        name doesn't already exist and that all required fields are present.
        
        Args:
            persona_data: Dictionary containing persona configuration with
                         keys: name, description, system_prompt, max_context_window,
                         routing_hint
            
        Returns:
            Dict representing the created persona with all configuration fields
            
        Raises:
            ValueError: If persona name already exists or required fields are missing
        """
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

    def update_persona(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing persona configuration.
        
        Modifies the configuration of an existing persona with the provided
        updates. Only updates fields that are not None in the updates dict.
        
        Args:
            name: Name of the persona to update
            updates: Dictionary containing fields to update (any combination of
                    description, system_prompt, max_context_window, routing_hint)
                    
        Returns:
            Dict representing the updated persona configuration
            
        Raises:
            ValueError: If persona doesn't exist or update field is invalid
        """
        if name not in self.config.personas:
            raise ValueError(f"Persona '{name}' not found")

        persona = self.config.personas[name]
        for key, value in updates.items():
            if value is not None:
                if not hasattr(persona, key):
                    raise ValueError(f"Persona config has no attribute '{key}'")
                setattr(persona, key, value)

        return self._persona_to_dict(name, persona)

    def delete_persona(self, name: str) -> bool:
        """Delete a persona configuration.
        
        Removes a persona from the configuration and from the allowed
        personas list. Logs a warning about the deletion.
        
        Args:
            name: Name of the persona to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            ValueError: If persona doesn't exist
        """
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

    def update_routing_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update routing configuration.
        
        Modifies the routing configuration including which personas are
        allowed for routing requests. Validates that all personas exist
        before updating the allowed list.
        
        Args:
            updates: Dictionary containing routing configuration updates:
                    - allowed_personas: List of persona names to allow
                    - enable_adaptive_routing: Boolean (currently placeholder)
                    
        Returns:
            Dict containing the updated routing configuration
            
        Raises:
            ValueError: If any specified persona doesn't exist
        """
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

    def update_context_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update context pipeline configuration.
        
        Modifies the configuration for the context processing pipeline
        including document directories, semantic chunking settings, and
        token limits.
        
        Args:
            updates: Dictionary containing context configuration updates:
                    - extra_documents_dir: Path to additional documents directory
                    - enable_semantic_chunking: Whether to enable semantic chunking
                    - max_combined_context_tokens: Maximum tokens for context
            
        Returns:
            Dict containing the updated context configuration
        """
        context_config = self.config.context_pipeline

        if "extra_documents_dir" in updates and updates["extra_documents_dir"] is not None:
            from pathlib import Path
            context_config.extra_documents_dir = Path(updates["extra_documents_dir"])

        if "enable_semantic_chunking" in updates and updates["enable_semantic_chunking"] is not None:
            context_config.enable_semantic_chunking = updates["enable_semantic_chunking"]

        if "max_combined_context_tokens" in updates and updates["max_combined_context_tokens"] is not None:
            context_config.max_combined_context_tokens = updates["max_combined_context_tokens"]

        return self.get_context_config()

    def test_backend(self, name: str) -> Dict[str, Any]:
        """Test connectivity and availability of a backend.
        
        Performs a connectivity test on the specified backend to determine
        if it's operational and measure response latency.
        
        Args:
            name: Name of the backend to test
            
        Returns:
            Dict containing:
            - success: Boolean indicating if backend is available
            - latency_ms: Response time in milliseconds
            - error: Error message if test failed, None if successful
            
        Raises:
            ValueError: If backend name is not found
        """
        import time
        backend = next((b for b in self.backends if b.name == name), None)

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

    def save_config(self) -> Dict[str, Any]:
        """Save current configuration to persistent storage.
        
        Currently creates a hash of the current configuration for validation
        purposes. Full persistent storage implementation would require writing
        to the configuration file, which is complex in a running system.
        
        Returns:
            Dict containing:
            - success: Boolean indicating if save operation succeeded
            - config_hash: Hash of the saved configuration
            - message: Status message about the save operation
        """
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

    def _persona_to_dict(self, name: str, persona) -> Dict[str, Any]:
        """Convert persona configuration to dictionary response format.
        
        Internal helper method that transforms a PersonaConfig object
        into the standard response format including active status.
        
        Args:
            name: Name of the persona
            persona: PersonaConfig object to convert
            
        Returns:
            Dict containing persona data in response format
        """
        return {
            "name": name,
            "description": persona.description,
            "system_prompt": persona.system_prompt,
            "max_context_window": persona.max_context_window,
            "routing_hint": persona.routing_hint,
            "is_active": name in self.config.allowed_personas
        }


__all__ = ["JarvisApplication"]
