"""Core configuration settings for Jarvis AI V2."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from config.config_loader import load_config as load_raw_config


# Default configuration
DEFAULT_CONFIG = {
    "enabled": True,
    "backend_url": "http://localhost:8001",
    "langgraph_checkpoint_path": "./checkpoints/jarvis_agent.db",
    "max_iterations": 15,
    "expert_model": "llama3.2",
    "use_langchain_tools": True,
    "fallback_to_v1": True,
    "workflow_visualization": True,
    "langgraphui_enabled": False,
}

# Model configuration
MODELS = {
    "default": "llama3.2",
    "fallback": "gpt-4o",
    "specialist": "llama3.2-70b",
}

# Tool configuration
TOOLS_ENABLED = [
    "search",
    "code_analysis",
    "web_browse",
    "file_management",
    "calculator",
]


class V2AgentConfig(BaseModel):
    """Settings specific to the v2 agent."""

    default_model: str = Field(default="llama3.2")
    enable_critics: bool = Field(default=True)


class Config(BaseModel):
    """Top-level application configuration."""

    model_config = ConfigDict(extra="allow")
    v2_agent: V2AgentConfig = Field(default_factory=V2AgentConfig)


def load_config() -> Config:
    """Load the application configuration as a Pydantic model."""

    data = load_raw_config()
    return Config(**data)


__all__ = [
    "Config",
    "V2AgentConfig",
    "load_config",
    "DEFAULT_CONFIG",
    "MODELS",
    "TOOLS_ENABLED",
]
