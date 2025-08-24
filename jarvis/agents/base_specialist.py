from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseSpecialist(ABC):
    """Abstract interface for specialist agents.

    Specialist implementations are expected to expose a ``specialization``
    attribute describing their domain of expertise and implement the
    :meth:`process_task` coroutine which performs work on behalf of the
    orchestrator.  A lightweight ``get_specialization_info`` method is also
    required so orchestrators can introspect capabilities without having to
    execute a task.
    """

    #: Descriptive name of the specialist domain (e.g. ``"security"``)
    specialization: str

    @abstractmethod
    async def process_task(
        self,
        task: str,
        context: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a task and return structured results.

        Parameters
        ----------
        task:
            Natural language description of the work to perform.
        context:
            Optional list of prior specialist outputs that may provide
            additional context for the current task.
        user_context:
            Optional free‑form string supplied by the user.
        """

    @abstractmethod
    def get_specialization_info(self) -> Dict[str, Any]:
        """Return metadata about the specialist such as supported domains or
        preferred models."""
