from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class OllamaConfig(BaseModel):
    host: str = Field("http://127.0.0.1:11434", description="Base URL for the local Ollama service")
    model: str = Field("llama3", description="Default Ollama model identifier")
    timeout: float = Field(30.0, ge=1.0, description="Request timeout in seconds")
    enable_ui: bool = Field(True, description="Expose the Ollama chat UI")


class WindowsMLConfig(BaseModel):
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
        if value in (None, ""):
            return None
        return Path(os.path.expanduser(str(value))).resolve()


class SecurityConfig(BaseModel):
    api_keys: List[str] = Field(default_factory=list, description="Static API keys allowed for API access")
    audit_log_path: Optional[Path] = Field(default=None, description="Optional path to persist security audit logs")

    @field_validator("api_keys", mode="before")
    @classmethod
    def _normalise_keys(cls, value: Any) -> List[str]:
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
    name: str
    description: str
    system_prompt: str
    max_context_window: int = Field(4096, ge=512)
    routing_hint: str = Field("general", description="Hint used by the routing pipeline")


class ContextPipelineConfig(BaseModel):
    extra_documents_dir: Optional[Path] = Field(
        default=None, description="Optional directory of additional documents to inject into context"
    )
    enable_semantic_chunking: bool = Field(True, description="Split documents into semantic chunks")
    max_combined_context_tokens: int = Field(8192, ge=1024)

    @field_validator("extra_documents_dir", mode="before")
    @classmethod
    def _expand_dir(cls, value: Any) -> Optional[Path]:
        if value in (None, ""):
            return None
        return Path(os.path.expanduser(str(value))).resolve()


class MonitoringConfig(BaseModel):
    enable_metrics_harvest: bool = Field(True, description="Enable harvesting of metrics and traces")
    harvest_interval_s: float = Field(30.0, ge=5.0)


class AppConfig(BaseModel):
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    windowsml: WindowsMLConfig = Field(default_factory=WindowsMLConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    personas: Dict[str, PersonaConfig] = Field(default_factory=dict)
    context_pipeline: ContextPipelineConfig = Field(default_factory=ContextPipelineConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    allowed_personas: List[str] = Field(default_factory=list)
    enable_research_features: bool = Field(True, description="Enable deep research workflows")

    @field_validator("personas", mode="after")
    @classmethod
    def _validate_personas(cls, value: Dict[str, PersonaConfig]) -> Dict[str, PersonaConfig]:
        if not value:
            default_persona = PersonaConfig(
                name="generalist",
                description="Balanced assistant persona",
                system_prompt=(
                    "You are Jarvis, a local-first research assistant. Provide concise, factual answers and highlight sources."
                ),
                max_context_window=4096,
            )
            value = {default_persona.name: default_persona}
        return value

    @field_validator("allowed_personas", mode="before")
    @classmethod
    def _default_allowed_personas(cls, value: List[str] | None, info: ValidationInfo) -> List[str]:
        if value:
            return value
        personas = info.data.get("personas", {}) if info and hasattr(info, "data") else {}
        if isinstance(personas, dict):
            return list(personas.keys())
        return []


def _config_env_paths() -> List[Path]:
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
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _merge_dict(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _merge_dict(dict(base[key]), value)
        else:
            base[key] = value
    return base


@lru_cache(maxsize=1)
def load_config(explicit_path: Optional[str] = None) -> AppConfig:
    base_data: Dict[str, Any] = {}
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        base_data = _load_json(path)
    else:
        for candidate in _config_env_paths():
            if candidate.exists():
                base_data = _merge_dict(base_data, _load_json(candidate))

    env_overrides: Dict[str, Any] = {}
    if host := os.getenv("OLLAMA_HOST"):
        env_overrides.setdefault("ollama", {})["host"] = host
    if model := os.getenv("OLLAMA_MODEL"):
        env_overrides.setdefault("ollama", {})["model"] = model
    if keys := os.getenv("JARVIS_API_KEYS"):
        env_overrides.setdefault("security", {})["api_keys"] = [k.strip() for k in keys.split(",") if k.strip()]
    if persona := os.getenv("JARVIS_DEFAULT_PERSONA"):
        env_overrides["allowed_personas"] = [persona]

    if env_overrides:
        base_data = _merge_dict(base_data, env_overrides)

    return AppConfig.model_validate(base_data)


__all__ = [
    "AppConfig",
    "OllamaConfig",
    "WindowsMLConfig",
    "SecurityConfig",
    "PersonaConfig",
    "ContextPipelineConfig",
    "MonitoringConfig",
    "load_config",
]
