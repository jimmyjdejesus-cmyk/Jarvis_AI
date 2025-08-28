"""Utilities for converting curiosity questions into mission directives."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CuriosityRouter:
    """Route curiosity questions into sanitized mission directives.

    The router prepends a short prefix and strips potentially unsafe
    characters to reduce the risk of injecting unintended commands.
    """

    prefix: str = "Investigate"

    def route(self, question: str) -> str:
        """Convert a question into a sanitized directive.

        Parameters
        ----------
        question: str
            Natural language question produced by :class:`CuriosityAgent`.

        Returns
        -------
        str
            Mission directive derived from the question.
        """
        cleaned = re.sub(r"[\r\n;]+", " ", question).strip().rstrip("?")
        return f"{self.prefix}: {cleaned}"


__all__ = ["CuriosityRouter"]
