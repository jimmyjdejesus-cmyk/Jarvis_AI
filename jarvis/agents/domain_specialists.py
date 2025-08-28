"""Domain-specific specialist agents.

These lightweight classes wrap
:class:`~jarvis.agents.specialist.SpecialistAgent` with concrete
specializations such as documentation, databases, security, and
localization. Interfaces stay small so new specialists need minimal
boilerplate.
"""
from __future__ import annotations

from typing import Any, Dict

from .specialist import SpecialistAgent
from jarvis.agents.agent_resources import AgentCapability
from jarvis.world_model.knowledge_graph import KnowledgeGraph


class DocumentationSpecialist(SpecialistAgent):
    """Produces technical documentation and summaries."""

    def __init__(
        self, mcp_client: Any, knowledge_graph: KnowledgeGraph | None = None
    ) -> None:
        super().__init__(
            agent_id="docs_specialist",
            specialization="docs",
            capabilities=[AgentCapability.ANALYSIS],
            knowledge_graph=knowledge_graph,
            mcp_client=mcp_client,
            preferred_models=["gpt-4", "claude-3.5-sonnet", "llama3.2"],
        )

    async def create_report(self, content: str) -> Dict[str, Any]:
        """Create a structured report from raw content."""
        task = f"**REPORT REQUEST**\n\n{content}"
        return await self.process_task(task)


class DatabaseSpecialist(SpecialistAgent):
    """Handles database design questions and SQL tuning."""

    def __init__(
        self, mcp_client: Any, knowledge_graph: KnowledgeGraph | None = None
    ) -> None:
        super().__init__(
            agent_id="database_specialist",
            specialization="database",
            capabilities=[AgentCapability.ANALYSIS],
            knowledge_graph=knowledge_graph,
            mcp_client=mcp_client,
            preferred_models=["gpt-4", "claude-3.5-sonnet", "llama3.2"],
        )

    async def optimize_query(
        self, query: str, schema: str | None = None
    ) -> Dict[str, Any]:
        """Suggest improvements for a SQL query."""
        schema_section = schema or "Schema not provided"
        task = (
            "**QUERY OPTIMIZATION REQUEST**\n\n"
            f"**Schema:**\n{schema_section}\n\n"
            "**Query:**\n```\n"
            f"{query}\n```"
        )
        return await self.process_task(task)


class SecuritySpecialist(SpecialistAgent):
    """Performs ethical hacking style assessments."""

    def __init__(
        self, mcp_client: Any, knowledge_graph: KnowledgeGraph | None = None
    ) -> None:
        super().__init__(
            agent_id="security_specialist",
            specialization="security",
            capabilities=[AgentCapability.ANALYSIS],
            knowledge_graph=knowledge_graph,
            mcp_client=mcp_client,
            preferred_models=["gpt-4", "claude-3.5-sonnet", "llama3.2"],
        )

    async def penetration_test(
        self, system_description: str
    ) -> Dict[str, Any]:
        """Simulate an adversarial penetration test."""
        task = f"**PENETRATION TEST REQUEST**\n\n{system_description}"
        return await self.process_task(task)


class LocalizationSpecialist(SpecialistAgent):
    """Translates and adapts content for specific locales."""

    def __init__(
        self, mcp_client: Any, knowledge_graph: KnowledgeGraph | None = None
    ) -> None:
        super().__init__(
            agent_id="localization_specialist",
            specialization="localization",
            capabilities=[AgentCapability.ANALYSIS],
            knowledge_graph=knowledge_graph,
            mcp_client=mcp_client,
            preferred_models=["gpt-4", "claude-3.5-sonnet", "llama3.2"],
        )

    async def translate_content(
        self, text: str, target_language: str
    ) -> Dict[str, Any]:
        """Translate text into the target language with localization notes."""
        task = (
            "**LOCALIZATION REQUEST**\n\n"
            f"**Target Language:** {target_language}\n\n"
            "**Content:**\n```\n"
            f"{text}\n```"
        )
        return await self.process_task(task)


class CodeReviewSpecialist(SpecialistAgent):
    """Performs lightweight code reviews."""

    def __init__(
        self, mcp_client: Any, knowledge_graph: KnowledgeGraph | None = None
    ) -> None:
        super().__init__(
            "codereview",
            mcp_client,
            agent_id="code_review_specialist",
            capabilities=[AgentCapability.ANALYSIS],
            knowledge_graph=knowledge_graph,
            preferred_models=["gpt-4", "claude-3.5-sonnet", "llama3.2"],
        )

    async def review_code(self, code: str) -> Dict[str, Any]:
        """Generate feedback for provided code."""
        task = f"**CODE REVIEW REQUEST**\n\n```\n{code}\n```"
        return await self.process_task(task)
