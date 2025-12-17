# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

from .base import GenerationRequest, GenerationResponse, LLMBackend
from ..logger import get_logger

logger = get_logger(__name__)


class OpenRouterBackend(LLMBackend):
    """Backend for OpenRouter API (Cloud Agent)."""

    def __init__(self, api_key: str, model: str = "openai/gpt-3.5-turbo", site_url: str = "", app_name: str = "AdaptiveMind Local"):
        self.name = "openrouter"
        self.api_key = api_key
        self.model = model
        self.site_url = site_url
        self.app_name = app_name
        self._base_url = "https://openrouter.ai/api/v1"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
            "Content-Type": "application/json",
        }

        # Construct messages with system prompt from persona
        messages = []
        # If context is provided, prepend it to the system prompt or first user message
        system_content = f"You are acting as the '{request.persona}' persona.\n\nContext:\n{request.context}"
        messages.append({"role": "system", "content": system_content})
        
        # Append conversation history
        for msg in request.messages:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                
                return GenerationResponse(
                    content=content,
                    tokens=total_tokens,
                    backend=self.name,
                    diagnostics={"model": self.model, "provider": "openrouter"}
                )
        except Exception as e:
            logger.error("OpenRouter generation failed", extra={"error": str(e)})
            # Return a fallback response or re-raise depending on strategy
            # For now, we return an error message as content to be handled by the router fallback
            raise e
