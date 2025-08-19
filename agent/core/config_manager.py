"""
Enhanced Configuration Management for Jarvis AI
Provides robust configuration handling with validation, defaults, and environment support.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import logging
from dataclasses import dataclass, field
from agent.core.error_handling import robust_operation, get_logger


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    cookie_secret_key: str = "change_this_secret_key"
    cookie_expiry_days: int = 30
    max_login_attempts: int = 5
    login_lockout_minutes: int = 15
    password_min_length: int = 8
    require_special_chars: bool = True
    session_timeout_minutes: int = 60
    enable_2fa: bool = False


@dataclass 
class PerformanceConfig:
    """Performance and optimization settings."""
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 30
    cache_size_mb: int = 100
    enable_caching: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = True
    max_log_file_size_mb: int = 50
    log_retention_days: int = 30


@dataclass
class RAGConfig:
    """RAG (Retrieval Augmented Generation) configuration."""
    enable_web_search: bool = True
    max_search_results: int = 5
    search_timeout_seconds: int = 10
    enable_file_context: bool = True
    max_file_size_mb: int = 10
    max_context_length: int = 8000
    enable_browser_automation: bool = True
    enable_human_in_loop: bool = True


@dataclass
class IntegrationConfig:
    """External integration settings."""
    enable_github: bool = True
    enable_notion: bool = False
    enable_onenote: bool = False
    enable_jetbrains: bool = True
    ollama_endpoint: str = "http://localhost:11434"
    default_model: str = "llama3"
    github_token: Optional[str] = None
    notion_token: Optional[str] = None


@dataclass
class JarvisConfig:
    """Main Jarvis AI configuration."""
    app_name: str = "Jarvis AI"
    version: str = "2.0.0"
    debug_mode: bool = False
    data_directory: str = "data"
    logs_directory: str = "logs"
    plugins_directory: str = "plugins"
    
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    
    # Custom settings
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigurationManager:
    """Enhanced configuration management with validation and environment support."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = get_logger()
        self.config_path = config_path or self._find_config_file()
        self.config = JarvisConfig()
        self._env_prefix = "JARVIS_"
        
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        possible_paths = [
            "config/config.yaml",
            "config/config.yml", 
            "jarvis_config.yaml",
            "jarvis_config.yml",
            os.path.expanduser("~/.jarvis/config.yaml"),
            "/etc/jarvis/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path if none found
        return "config/config.yaml"
    
    @robust_operation(operation_name="load_configuration")
    def load_config(self) -> JarvisConfig:
        """Load configuration from file with environment variable overrides."""
        # Load from file if exists
        if os.path.exists(self.config_path):
            self._load_from_file()
        else:
            self.logger.logger.warning(f"Config file {self.config_path} not found, using defaults")
        
        # Apply environment variable overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_config()
        
        # Create necessary directories
        self._create_directories()
        
        self.logger.logger.info("Configuration loaded successfully")
        return self.config
    
    def _load_from_file(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.json'):
                    config_data = json.load(f)
                else:
                    config_data = yaml.safe_load(f) or {}
            
            # Update configuration with file data
            self._update_config_from_dict(config_data)
            
        except Exception as e:
            self.logger.logger.error(f"Error loading config file {self.config_path}: {e}")
            raise
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration object from dictionary."""
        # Update main config attributes
        for key, value in config_data.items():
            if hasattr(self.config, key) and key != 'custom':
                if key in ['security', 'performance', 'rag', 'integrations']:
                    # Update nested config objects
                    nested_config = getattr(self.config, key)
                    if isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            if hasattr(nested_config, nested_key):
                                setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self.config, key, value)
            elif key == 'custom':
                self.config.custom.update(value if isinstance(value, dict) else {})
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides."""
        # Define environment variable mappings
        env_mappings = {
            f"{self._env_prefix}DEBUG": ("debug_mode", bool),
            f"{self._env_prefix}DATA_DIR": ("data_directory", str),
            f"{self._env_prefix}LOGS_DIR": ("logs_directory", str),
            f"{self._env_prefix}LOG_LEVEL": ("performance.log_level", str),
            f"{self._env_prefix}OLLAMA_ENDPOINT": ("integrations.ollama_endpoint", str),
            f"{self._env_prefix}DEFAULT_MODEL": ("integrations.default_model", str),
            f"{self._env_prefix}GITHUB_TOKEN": ("integrations.github_token", str),
            f"{self._env_prefix}COOKIE_SECRET": ("security.cookie_secret_key", str),
            f"{self._env_prefix}SESSION_TIMEOUT": ("security.session_timeout_minutes", int),
            f"{self._env_prefix}ENABLE_WEB_SEARCH": ("rag.enable_web_search", bool),
            f"{self._env_prefix}MAX_SEARCH_RESULTS": ("rag.max_search_results", int),
        }
        
        for env_var, (config_path, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # Convert value to appropriate type
                    if value_type == bool:
                        converted_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        converted_value = int(env_value)
                    else:
                        converted_value = env_value
                    
                    # Set nested configuration value
                    self._set_nested_config(config_path, converted_value)
                    
                except Exception as e:
                    self.logger.logger.warning(f"Invalid environment variable {env_var}={env_value}: {e}")
    
    def _set_nested_config(self, path: str, value: Any):
        """Set nested configuration value using dot notation."""
        parts = path.split('.')
        current = self.config
        
        for part in parts[:-1]:
            current = getattr(current, part)
        
        setattr(current, parts[-1], value)
    
    def _validate_config(self):
        """Validate configuration values."""
        errors = []
        
        # Validate security settings
        if len(self.config.security.cookie_secret_key) < 16:
            errors.append("Cookie secret key must be at least 16 characters")
        
        if self.config.security.password_min_length < 6:
            errors.append("Password minimum length must be at least 6")
        
        # Validate performance settings
        if self.config.performance.max_concurrent_requests < 1:
            errors.append("Max concurrent requests must be at least 1")
        
        if self.config.performance.request_timeout_seconds < 5:
            errors.append("Request timeout must be at least 5 seconds")
        
        # Validate RAG settings
        if self.config.rag.max_search_results < 1:
            errors.append("Max search results must be at least 1")
        
        if self.config.rag.max_file_size_mb < 1:
            errors.append("Max file size must be at least 1 MB")
        
        # Validate integration settings
        if not self.config.integrations.ollama_endpoint.startswith(('http://', 'https://')):
            errors.append("Ollama endpoint must be a valid URL")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            self.logger.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _create_directories(self):
        """Create necessary directories."""
        directories = [
            self.config.data_directory,
            self.config.logs_directory,
            self.config.plugins_directory,
            os.path.dirname(self.config_path)
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    self.logger.logger.info(f"Created directory: {directory}")
                except Exception as e:
                    self.logger.logger.warning(f"Could not create directory {directory}: {e}")
    
    @robust_operation(operation_name="save_configuration")
    def save_config(self, config: Optional[JarvisConfig] = None):
        """Save configuration to file."""
        if config:
            self.config = config
        
        # Convert config to dictionary
        config_dict = self._config_to_dict()
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Save to file
        with open(self.config_path, 'w') as f:
            if self.config_path.endswith('.json'):
                json.dump(config_dict, f, indent=2, default=str)
            else:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        self.logger.logger.info(f"Configuration saved to {self.config_path}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration object to dictionary."""
        config_dict = {
            "app_name": self.config.app_name,
            "version": self.config.version,
            "debug_mode": self.config.debug_mode,
            "data_directory": self.config.data_directory,
            "logs_directory": self.config.logs_directory,
            "plugins_directory": self.config.plugins_directory,
            "security": {
                "cookie_secret_key": self.config.security.cookie_secret_key,
                "cookie_expiry_days": self.config.security.cookie_expiry_days,
                "max_login_attempts": self.config.security.max_login_attempts,
                "login_lockout_minutes": self.config.security.login_lockout_minutes,
                "password_min_length": self.config.security.password_min_length,
                "require_special_chars": self.config.security.require_special_chars,
                "session_timeout_minutes": self.config.security.session_timeout_minutes,
                "enable_2fa": self.config.security.enable_2fa,
            },
            "performance": {
                "max_concurrent_requests": self.config.performance.max_concurrent_requests,
                "request_timeout_seconds": self.config.performance.request_timeout_seconds,
                "cache_size_mb": self.config.performance.cache_size_mb,
                "enable_caching": self.config.performance.enable_caching,
                "log_level": self.config.performance.log_level,
                "enable_metrics": self.config.performance.enable_metrics,
                "max_log_file_size_mb": self.config.performance.max_log_file_size_mb,
                "log_retention_days": self.config.performance.log_retention_days,
            },
            "rag": {
                "enable_web_search": self.config.rag.enable_web_search,
                "max_search_results": self.config.rag.max_search_results,
                "search_timeout_seconds": self.config.rag.search_timeout_seconds,
                "enable_file_context": self.config.rag.enable_file_context,
                "max_file_size_mb": self.config.rag.max_file_size_mb,
                "max_context_length": self.config.rag.max_context_length,
                "enable_browser_automation": self.config.rag.enable_browser_automation,
                "enable_human_in_loop": self.config.rag.enable_human_in_loop,
            },
            "integrations": {
                "enable_github": self.config.integrations.enable_github,
                "enable_notion": self.config.integrations.enable_notion,
                "enable_onenote": self.config.integrations.enable_onenote,
                "enable_jetbrains": self.config.integrations.enable_jetbrains,
                "ollama_endpoint": self.config.integrations.ollama_endpoint,
                "default_model": self.config.integrations.default_model,
                "github_token": self.config.integrations.github_token,
                "notion_token": self.config.integrations.notion_token,
            },
            "custom": self.config.custom
        }
        
        return config_dict
    
    def get_config(self) -> JarvisConfig:
        """Get current configuration."""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values."""
        self._update_config_from_dict(updates)
        self._validate_config()
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = JarvisConfig()
        self.save_config()
        self.logger.logger.info("Configuration reset to defaults")


# Global configuration manager instance
_config_manager = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
        _config_manager.load_config()
    return _config_manager


def get_config() -> JarvisConfig:
    """Get current configuration."""
    return get_config_manager().get_config()


def update_config(updates: Dict[str, Any]):
    """Update global configuration."""
    get_config_manager().update_config(updates)