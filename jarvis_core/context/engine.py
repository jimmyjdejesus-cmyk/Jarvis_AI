# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from ..config import AppConfig, PersonaConfig
from ..logger import get_logger

logger = get_logger(__name__)


@dataclass
class ContextSection:
    title: str
    body: str

    def token_length(self) -> int:
        return max(1, len(self.body.split()))


class ContextEngine:
    """Context engineering pipeline that enriches prompts for the LLMs."""

    def __init__(self, config: AppConfig):
        self._config = config

    def build_context(self, persona: PersonaConfig, messages: Sequence[dict], external_context: Iterable[str] | None = None) -> str:
        sections: List[ContextSection] = [
            ContextSection("Persona", persona.system_prompt),
            self._conversation_section(messages),
        ]
        if external_context:
            sections.append(self._external_section(external_context))
        if self._config.context_pipeline.extra_documents_dir:
            sections.extend(self._document_sections())
        ordered = self._truncate(sections, persona.max_context_window)
        return "\n\n".join(f"## {section.title}\n{section.body}" for section in ordered)

    def _conversation_section(self, messages: Sequence[dict]) -> ContextSection:
        normalized = []
        for message in messages[-20:]:
            role = message.get("role", "user").lower()
            content = message.get("content", "").strip()
            normalized.append(f"{role.upper()}: {content}")
        body = "\n".join(normalized)
        return ContextSection("Conversation", body)

    def _external_section(self, snippets: Iterable[str]) -> ContextSection:
        cleaned = [self._sanitize(snippet) for snippet in snippets if snippet.strip()]
        return ContextSection("Research", "\n".join(cleaned))

    def _document_sections(self) -> List[ContextSection]:
        directory = self._config.context_pipeline.extra_documents_dir
        if not directory or not directory.exists():
            return []
        sections: List[ContextSection] = []
        for path in itertools.islice(sorted(directory.glob("**/*.txt")), 0, 5):
            try:
                with path.open("r", encoding="utf-8") as handle:
                    content = handle.read().strip()
            except OSError:
                logger.warning("Failed to read context document", extra={"path": str(path)})
                continue
            sections.append(ContextSection(title=f"Doc:{path.stem}", body=self._sanitize(content)))
        return sections

    def _truncate(self, sections: Sequence[ContextSection], max_tokens: int) -> List[ContextSection]:
        result: List[ContextSection] = []
        running_total = 0
        for section in sections:
            tokens = section.token_length()
            if running_total + tokens > max_tokens:
                logger.debug(
                    "Context truncated", extra={"section": section.title, "running_total": running_total, "max": max_tokens}
                )
                break
            result.append(section)
            running_total += tokens
        return result

    def _sanitize(self, value: str) -> str:
        value = value.replace("\r\n", "\n").replace("\r", "\n")
        value = re.sub(r"\s+", " ", value)
        return value.strip()


__all__ = ["ContextEngine", "ContextSection"]
