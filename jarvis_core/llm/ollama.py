from __future__ import annotations

import json
import time
from typing import Dict

import requests

from .base import GenerationRequest, GenerationResponse, LLMBackend


class OllamaBackend(LLMBackend):
    """Backend that interacts with a local Ollama instance via HTTP."""

    name = "ollama"

    def __init__(self, host: str, model: str, timeout: float = 30.0):
        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._last_health_check: float = 0.0
        self._health_cache: bool = False

    def is_available(self) -> bool:
        now = time.time()
        if now - self._last_health_check < 10:
            return self._health_cache
        try:
            response = requests.get(f"{self._host}/api/tags", timeout=self._timeout)
            response.raise_for_status()
            data = response.json()
            models = {entry.get("name") for entry in data.get("models", [])}
            self._health_cache = self._model in models
        except Exception:
            self._health_cache = False
        self._last_health_check = now
        return self._health_cache

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        payload: Dict[str, object] = {
            "model": self._model,
            "prompt": request.context,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        http_response = requests.post(
            f"{self._host}/api/generate",
            json=payload,
            timeout=self._timeout,
        )
        http_response.raise_for_status()
        data = http_response.json()
        message = data.get("response") or data.get("content") or ""
        tokens = data.get("eval_count") or len(message.split())
        diagnostics = {
            "model": data.get("model", self._model),
            "total_duration": str(data.get("total_duration")),
        }
        return GenerationResponse(content=message, tokens=int(tokens), backend=self.name, diagnostics=diagnostics)


__all__ = ["OllamaBackend"]
