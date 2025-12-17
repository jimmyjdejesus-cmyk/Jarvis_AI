# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

import json
import time
from typing import Dict, Iterator

import requests

from .base import GenerationChunk, GenerationRequest, GenerationResponse, LLMBackend


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

    def stream(self, request: GenerationRequest) -> Iterator[GenerationChunk]:
        payload: Dict[str, object] = {
            "model": self._model,
            "prompt": request.context,
            "stream": True,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        http_response = requests.post(
            f"{self._host}/api/generate",
            json=payload,
            timeout=self._timeout,
            stream=True,
        )
        http_response.raise_for_status()
        full_content = ""
        total_tokens = 0
        for line in http_response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                chunk_content = data.get("response", "")
                full_content += chunk_content
                total_tokens = data.get("eval_count", total_tokens)
                finished = data.get("done", False)
                diagnostics = {
                    "model": data.get("model", self._model),
                    "total_duration": str(data.get("total_duration", "")),
                }
                yield GenerationChunk(
                    content=chunk_content,
                    tokens=total_tokens,
                    backend=self.name,
                    finished=finished,
                    diagnostics=diagnostics,
                )
                if finished:
                    break


__all__ = ["OllamaBackend"]
