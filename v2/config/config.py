"""Core configuration settings for Jarvis AI V2."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from pathlib import Path
from typing import Dict

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

    model_config = ConfigDict(extra="allow")
    default_model: str = Field(default="llama3.2")
    enable_red_team: bool = Field(default=True)
    enable_blue_team: bool = Field(default=True)


class Config(BaseModel):
    """Top-level application configuration."""

    model_config = ConfigDict(extra="allow")
    v2_agent: V2AgentConfig = Field(default_factory=V2AgentConfig)


def load_config() -> Config:
    """Load the application configuration as a Pydantic model."""

    data = load_raw_config()
    return Config(**data)


def save_secrets(secrets: Dict[str, str]) -> None:
    """Persist secret values to the local .env file."""
    env_path = Path(".env")
    existing: Dict[str, str] = {}

    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            existing[key] = value

    existing.update(secrets)

    with env_path.open("w") as fh:
        for key, value in existing.items():
            fh.write(f"{key}={value}\n")


__all__ = [
    "Config",
    "V2AgentConfig",
    "load_config",
    "save_secrets",
    "DEFAULT_CONFIG",
    "MODELS",
    "TOOLS_ENABLED",
]
