# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/




Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

"""Enhanced config loader that provides robust configuration management.

This module serves as the main configuration loading interface for the Jarvis
application, providing comprehensive configuration management with validation,
environment variable support, and intelligent defaults.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import ValidationError

try:
    # Import the comprehensive configuration system
    from jarvis_core.config import (
        AppConfig, 
        OllamaConfig, 
        OpenRouterConfig, 
        WindowsMLConfig, 
        SecurityConfig, 
        PersonaConfig,
        ContextPipelineConfig,
        MonitoringConfig
    )
    COMPREHENSIVE_CONFIG_AVAILABLE = True
except ImportError:
    # Fallback to basic types if comprehensive config is not available
    from typing import TypedDict
    
    class BasicConfig(TypedDict):
        ollama: Dict[str, Any]
        openrouter: Dict[str, Any]  
        windowsml: Dict[str, Any]
        security: Dict[str, Any]
        personas: Dict[str, Any]
        context_pipeline: Dict[str, Any]
        monitoring: Dict[str, Any]
        allowed_personas: list
        enable_research_features: bool
    
    COMPREHENSIVE_CONFIG_AVAILABLE = False


def _load_json_config(path: Path) -> Dict[str, Any]:
    """Load and parse JSON configuration file.
    
    Args:
        path: Path to JSON configuration file
        
    Returns:
        Parsed configuration dictionary
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        print(f"Warning: Could not load config from {path}: {e}")
        return {}


def _discover_config_paths() -> list[Path]:
    """Discover configuration file paths from standard locations.
    
    Returns:
        List of discovered configuration file paths
    """
    candidates = [
        os.getenv("ADAPTIVEMIND_CONFIG"),
        os.getenv("ADAPTIVEMIND_HOME"),
        os.path.join(os.path.expanduser("~"), ".jarvis", "config.json"),
        os.path.join(os.path.expanduser("~"), ".config", "jarvis", "config.json"),
        "config.json",
        "adaptivemind_config.json"
    ]
    
    paths = []
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


def _create_default_config() -> Dict[str, Any]:
    """Create a default configuration dictionary.
    
    Returns:
        Default configuration with sensible defaults
    """
    return {
        "ollama": {
            "host": "http://127.0.0.1:11434",
            "model": "llama3",
            "timeout": 30.0,
            "enable_ui": True
        },
        "openrouter": {
            "api_key": "",
            "model": "openai/gpt-3.5-turbo",
            "site_url": "",
            "app_name": "AdaptiveMind Local"
        },
        "windowsml": {
            "enabled": False,
            "model_path": None,
            "device_preference": "cpu"
        },
        "security": {
            "api_keys": [],
            "audit_log_path": None
        },
        "personas": {
            "generalist": {
                "name": "generalist",
                "description": "Balanced assistant persona",
                "system_prompt": "You are AdaptiveMind, a local-first research assistant. Provide concise, factual answers and highlight sources.",
                "max_context_window": 4096,
                "routing_hint": "general"
            }
        },
        "context_pipeline": {
            "extra_documents_dir": None,
            "enable_semantic_chunking": True,
            "max_combined_context_tokens": 8192
        },
        "monitoring": {
            "enable_metrics_harvest": True,
            "harvest_interval_s": 30.0
        },
        "allowed_personas": ["generalist"],
        "enable_research_features": True
    }


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration.
    
    Args:
        config: Base configuration dictionary
        
    Returns:
        Configuration with environment overrides applied
    """
    # Ollama overrides
    if host := os.getenv("OLLAMA_HOST"):
        config.setdefault("ollama", {})["host"] = host
    if model := os.getenv("OLLAMA_MODEL"):
        config.setdefault("ollama", {})["model"] = model
        
    # OpenRouter overrides
    if api_key := os.getenv("OPENROUTER_API_KEY"):
        config.setdefault("openrouter", {})["api_key"] = api_key
        
    # Security overrides
    if api_keys := os.getenv("ADAPTIVEMIND_API_KEYS"):
        keys = [k.strip() for k in api_keys.split(",") if k.strip()]
        config.setdefault("security", {})["api_keys"] = keys
        
    # Default persona override
    if default_persona := os.getenv("ADAPTIVEMIND_DEFAULT_PERSONA"):
        config["allowed_personas"] = [default_persona]
        
    return config


def load_config(explicit_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from multiple sources with intelligent fallbacks.
    
    Configuration loading priority:
    1. Explicit file path (if provided)
    2. Environment variable file paths
    3. Standard config file locations
    4. Environment variable overrides
    5. Default configuration
    
    Args:
        explicit_path: Optional explicit path to configuration file
        
    Returns:
        Configuration dictionary with all sources merged
    """
    config = _create_default_config()
    
    # Load from explicit path if provided
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        if path.exists():
            file_config = _load_json_config(path)
            config.update(file_config)
    else:
        # Load from discovered config files
        for config_path in _discover_config_paths():
            file_config = _load_json_config(config_path)
            if file_config:
                config.update(file_config)
                break  # Use first found config file
    
    # Apply environment variable overrides
    config = _apply_env_overrides(config)
    
    # If comprehensive config is available, validate and return as AppConfig
    if COMPREHENSIVE_CONFIG_AVAILABLE:
        try:
            validated_config = AppConfig.model_validate(config)
            return validated_config.model_dump()
        except ValidationError as e:
            print(f"Warning: Configuration validation failed: {e}")
            print("Using partial configuration with defaults")
    
    return config


# Export the comprehensive config loader if available
if COMPREHENSIVE_CONFIG_AVAILABLE:
    def load_app_config(explicit_path: Optional[str] = None) -> AppConfig:
        """Load configuration as a validated AppConfig object.
        
        Args:
            explicit_path: Optional explicit path to configuration file
            
        Returns:
            Validated AppConfig instance
            
        Raises:
            ValidationError: If configuration validation fails
        """
        config_dict = load_config(explicit_path)
        return AppConfig.model_validate(config_dict)
else:
    def load_app_config(explicit_path: Optional[str] = None) -> Dict[str, Any]:
        """Fallback loader when comprehensive config is not available.
        
        Args:
            explicit_path: Optional explicit path to configuration file
            
        Returns:
            Configuration dictionary
        """
        return load_config(explicit_path)


__all__ = ["load_config", "load_app_config"]
