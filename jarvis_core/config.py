"""Configuration management module for Jarvis Core.

This module provides comprehensive configuration management for the Jarvis
application using Pydantic models for validation and serialization. It handles
configuration loading from multiple sources including files, environment
variables, and provides intelligent defaults and validation.

Key features:
- Hierarchical configuration with validation
- Environment variable overrides
- Path expansion and resolution
- API key validation and normalization
- Default persona generation
- Config caching for performance
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class OllamaConfig(BaseModel):
    """Configuration for local Ollama model hosting.
    
    Manages settings for connecting to and using local Ollama instances
    for running models locally without external API dependencies.
    
    Attributes:
        host: Base URL for the local Ollama service
        model: Default Ollama model identifier to use
        timeout: Request timeout in seconds for Ollama API calls
        enable_ui: Whether to expose the Ollama chat UI
    """
    host: str = Field("http://127.0.0.1:11434", description="Base URL for the local Ollama service")
    model: str = Field("llama3", description="Default Ollama model identifier")
    timeout: float = Field(30.0, ge=1.0, description="Request timeout in seconds")
    enable_ui: bool = Field(True, description="Expose the Ollama chat UI")


class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter cloud-based model access.
    
    Manages settings for connecting to OpenRouter which provides access
    to various commercial and open-source models via a unified API.
    
    Attributes:
        api_key: OpenRouter API key for authentication
        model: Default OpenRouter model to use
        site_url: Site URL for OpenRouter rankings and attribution
        app_name: Application name for OpenRouter rankings
    """
    api_key: str = Field("", description="OpenRouter API Key")
    model: str = Field("openai/gpt-3.5-turbo", description="Default OpenRouter model")
    site_url: str = Field("", description="Site URL for OpenRouter rankings")
    app_name: str = Field("Jarvis Local", description="App name for OpenRouter rankings")


class WindowsMLConfig(BaseModel):
    """Configuration for WindowsML/ONNX Runtime acceleration.
    
    Manages settings for local ONNX model inference using WindowsML
    or ONNX Runtime for accelerated inference on supported hardware.
    
    Attributes:
        enabled: Whether to enable WindowsML fallback acceleration
        model_path: Path to ONNX model for local inference
        device_preference: Preferred execution provider (cpu, dml)
    """
    enabled: bool = Field(False, description="Enable WindowsML fallback acceleration")
    model_path: Optional[Path] = Field(
        default=None, description="Path to an ONNX model consumable by WindowsML/ONNX Runtime"
    )
    device_preference: str = Field(
        "cpu",
        description="Preferred execution provider (cpu, dml). cpu is always available, dml requires DirectML",
    )

    @field_validator("model_path", mode="before")
    @classmethod
    def _expand_model_path(cls, value: Any) -> Optional[Path]:
        """Expand and resolve model path from environment variables and ~."""
        if value in (None, ""):
            return None
        return Path(os.path.expanduser(str(value))).resolve()


class SecurityConfig(BaseModel):
    """Configuration for security and access control.
    
    Manages security-related settings including API key authentication
    and audit logging configuration.
    
    Attributes:
        api_keys: List of static API keys allowed for API access
        audit_log_path: Optional path to persist security audit logs
    """
    api_keys: List[str] = Field(default_factory=list, description="Static API keys allowed for API access")
    audit_log_path: Optional[Path] = Field(default=None, description="Optional path to persist security audit logs")

    @field_validator("api_keys", mode="before")
    @classmethod
    def _normalise_keys(cls, value: Any) -> List[str]:
        """Normalize and validate API keys from various input formats.
        
        Accepts API keys as:
        - List of strings
        - Comma-separated string
        - None/empty (returns empty list)
        
        Returns:
            List of non-empty, trimmed API key strings
            
        Raises:
            TypeError: If input is not a list or string
            ValueError: If any API key is empty after trimming
        """
        if value in (None, ""):
            return []
        if isinstance(value, str):
            value = [v for v in value.split(",")]
        if not isinstance(value, list):
            raise TypeError("api_keys must be a list or comma separated string")
        cleaned: List[str] = []
        for item in value:
            candidate = str(item).strip()
            if not candidate:
                raise ValueError("API keys must be non-empty strings")
            cleaned.append(candidate)
        return cleaned


class PersonaConfig(BaseModel):
    """Configuration for AI persona definitions.
    
    Defines how different AI personas should behave, including their
    system prompts, context windows, and routing preferences.
    
    Attributes:
        name: Unique identifier for the persona
        description: Human-readable description of persona behavior
        system_prompt: System prompt that defines persona behavior
        max_context_window: Maximum tokens this persona can handle
        routing_hint: Hint used by routing pipeline for backend selection
    """
    name: str
    description: str
    system_prompt: str
    max_context_window: int = Field(4096, ge=512)
    routing_hint: str = Field("general", description="Hint used by the routing pipeline")


class ContextPipelineConfig(BaseModel):
    """Configuration for context processing pipeline.
    
    Manages settings for document loading, semantic chunking, and
    context token management for retrieval-augmented generation.
    
    Attributes:
        extra_documents_dir: Directory containing additional documents for context
        enable_semantic_chunking: Whether to split documents into semantic chunks
        max_combined_context_tokens: Maximum total tokens for combined context
    """
    extra_documents_dir: Optional[Path] = Field(
        default=None, description="Optional directory of additional documents to inject into context"
    )
    enable_semantic_chunking: bool = Field(True, description="Split documents into semantic chunks")
    max_combined_context_tokens: int = Field(8192, ge=1024)

    @field_validator("extra_documents_dir", mode="before")
    @classmethod
    def _expand_dir(cls, value: Any) -> Optional[Path]:
        """Expand and resolve document directory path."""
        if value in (None, ""):
            return None
        return Path(os.path.expanduser(str(value))).resolve()


class MonitoringConfig(BaseModel):
    """Configuration for system monitoring and metrics.
    
    Manages settings for performance monitoring, metrics collection,
    and automated harvesting of system statistics.
    
    Attributes:
        enable_metrics_harvest: Whether to enable metrics and trace harvesting
        harvest_interval_s: Interval in seconds between metric harvests
    """
    enable_metrics_harvest: bool = Field(True, description="Enable harvesting of metrics and traces")
    harvest_interval_s: float = Field(30.0, ge=5.0)


def _default_personas() -> Dict[str, PersonaConfig]:
    """Create default persona configurations.
    
    Returns a dictionary containing the default 'generalist' persona
    configuration that provides balanced assistant behavior.
    
    Returns:
        Dict mapping persona name to PersonaConfig object
    """
    default_persona = PersonaConfig(
        name="generalist",
        description="Balanced assistant persona",
        system_prompt=(
            "You are Jarvis, a local-first research assistant. Provide concise, factual answers and highlight sources."
        ),
        max_context_window=4096,
    )
    return {default_persona.name: default_persona}


class AppConfig(BaseModel):
    """Main application configuration container.
    
    Aggregates all configuration sections and provides validation
    for the complete Jarvis application setup.
    
    Attributes:
        ollama: Ollama backend configuration
        openrouter: OpenRouter backend configuration
        windowsml: WindowsML/ONNX configuration
        security: Security and access control configuration
        personas: Dictionary of persona configurations
        context_pipeline: Context processing pipeline configuration
        monitoring: System monitoring configuration
        allowed_personas: List of personas permitted for routing
        enable_research_features: Whether to enable deep research workflows
    """
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    openrouter: OpenRouterConfig = Field(default_factory=OpenRouterConfig)
    windowsml: WindowsMLConfig = Field(default_factory=WindowsMLConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    personas: Dict[str, PersonaConfig] = Field(default_factory=_default_personas)
    context_pipeline: ContextPipelineConfig = Field(default_factory=ContextPipelineConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    allowed_personas: List[str] = Field(default_factory=list)
    enable_research_features: bool = Field(True, description="Enable deep research workflows")

    @field_validator("allowed_personas", mode="after")
    @classmethod
    def _default_allowed_personas(cls, value: List[str] | None, info: ValidationInfo) -> List[str]:
        """Set default allowed personas from configured personas if not explicitly set.
        
        If allowed_personas is not provided, automatically include all
        configured personas to maintain backward compatibility.
        
        Args:
            value: Provided allowed_personas list (may be None)
            info: Validation context containing other field values
            
        Returns:
            List of allowed persona names
        """
        if value:
            return value
        personas = info.data.get("personas", {})
        if isinstance(personas, dict):
            return list(personas.keys())
        return []


def _config_env_paths() -> List[Path]:
    """Discover configuration file paths from environment and standard locations.
    
    Searches for configuration files in the following order:
    1. JARVIS_CONFIG environment variable (file path)
    2. JARVIS_HOME environment variable (directory with config.json)
    3. ~/.jarvis directory (config.json)
    
    Returns:
        List of discovered configuration file paths
    """
    candidates: List[str] = [
        os.getenv("JARVIS_CONFIG"),
        os.getenv("JARVIS_HOME"),
        os.path.join(os.path.expanduser("~"), ".jarvis"),
    ]
    paths: List[Path] = []
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file():
            paths.append(path)
        elif path.is_dir():
            config_file = path / "config.json"
            if config_file.exists():
                paths.append(config_file)
    return paths


def _load_json(path: Path) -> Dict[str, Any]:
    """Load and parse JSON configuration file.
    
    Args:
        path: Path to JSON configuration file
        
    Returns:
        Parsed configuration dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _merge_dict(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge overlay dictionary into base dictionary.
    
    Performs deep merge where nested dictionaries are merged rather
    than replaced, allowing partial configuration overrides.
    
    Args:
        base: Base configuration dictionary to merge into
        overlay: Override configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _merge_dict(dict(base[key]), value)
        else:
            base[key] = value
    return base


@lru_cache(maxsize=1)
def load_config(explicit_path: Optional[str] = None) -> AppConfig:
    """Load complete application configuration from multiple sources.
    
    Configuration loading priority (highest to lowest):
    1. Explicit file path (if provided)
    2. Environment variable files (JARVIS_CONFIG, JARVIS_HOME, ~/.jarvis)
    3. Environment variable overrides
    4. Default values from AppConfig model
    
    Environment variable overrides supported:
    - OLLAMA_HOST: Override Ollama service URL
    - OLLAMA_MODEL: Override default Ollama model
    - OPENROUTER_API_KEY: Override OpenRouter API key
    - JARVIS_API_KEYS: Override security API keys (comma-separated)
    - JARVIS_DEFAULT_PERSONA: Set default allowed persona
    
    Args:
        explicit_path: Optional explicit path to configuration file
        
    Returns:
        Validated AppConfig instance
        
    Raises:
        FileNotFoundError: If explicit config file doesn't exist
        ValidationError: If configuration validation fails
    """
    base_data: Dict[str, Any] = {}
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        base_data = _load_json(path)
    else:
        # Load from discovered config files
        for candidate in _config_env_paths():
            if candidate.exists():
                base_data = _merge_dict(base_data, _load_json(candidate))

    # Apply environment variable overrides
    env_overrides: Dict[str, Any] = {}
    if host := os.getenv("OLLAMA_HOST"):
        env_overrides.setdefault("ollama", {})["host"] = host
    if model := os.getenv("OLLAMA_MODEL"):
        env_overrides.setdefault("ollama", {})["model"] = model
    if or_key := os.getenv("OPENROUTER_API_KEY"):
        env_overrides.setdefault("openrouter", {})["api_key"] = or_key
    if keys := os.getenv("JARVIS_API_KEYS"):
        env_overrides.setdefault("security", {})["api_keys"] = [k.strip() for k in keys.split(",") if k.strip()]
    if persona := os.getenv("JARVIS_DEFAULT_PERSONA"):
        env_overrides["allowed_personas"] = [persona]

    if env_overrides:
        base_data = _merge_dict(base_data, env_overrides)

    # Validate and return final configuration
    return AppConfig.model_validate(base_data)


__all__ = [
    "AppConfig",
    "OllamaConfig",
    "OpenRouterConfig",
    "WindowsMLConfig",
    "SecurityConfig",
    "PersonaConfig",
    "ContextPipelineConfig",
    "MonitoringConfig",
    "load_config",
]
