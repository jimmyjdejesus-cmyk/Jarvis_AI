# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

import textwrap
from collections import Counter
from typing import Sequence

from .base import GenerationRequest, GenerationResponse, LLMBackend


class ContextualFallbackLLM(LLMBackend):
    """Deterministic fallback model that summarizes the conversation context."""

    name = "contextual-fallback"

    def is_available(self) -> bool:  # noqa: D401 - interface requirement
        return True

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        last_user_message = next((msg["content"] for msg in reversed(request.messages) if msg.get("role") == "user"), "")
        persona_summary = request.context.split("\n", 1)[0]
        token_estimate = len(request.context.split())
        keywords = self._top_keywords(request.context)
        content = textwrap.dedent(
            f"""
            Persona focus: {persona_summary}
            Most recent user request: {last_user_message}
            Key context terms: {', '.join(keywords)}
            Response: Based on the available local context, here is a structured summary and recommended next steps.
            - Context Window Size: {token_estimate} tokens (approx.)
            - Suggested Actions: Verify facts, consult linked research snippets, and prepare citations before responding.
            - Safety: Ensure API usage complies with configured policies and redact sensitive data.
            """
        ).strip()
        return GenerationResponse(content=content, tokens=len(content.split()), backend=self.name, diagnostics=None)

    def _top_keywords(self, context: str, limit: int = 5) -> Sequence[str]:
        tokens = [token.lower() for token in context.split() if token.isalpha()]
        if not tokens:
            return ()
        counts = Counter(tokens)
        return tuple(token for token, _ in counts.most_common(limit))


__all__ = ["ContextualFallbackLLM"]
