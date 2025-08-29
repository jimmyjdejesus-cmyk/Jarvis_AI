"""Simple LLM generator for Galaxy Model tests.

This module provides a placeholder implementation for generating reasoning
traces.  In production the ``generate_k_traces`` function should interface
with a vLLM server or other large language model to obtain diverse outputs.
"""

from __future__ import annotations

import random
from typing import List


def generate_k_traces(prompt: str, k: int) -> List[str]:
    """Return ``k`` deterministic reasoning traces for ``prompt``.

    A hash of the prompt seeds a local pseudo-random generator so that the
    generated traces are repeatable for tests.  Each trace concludes with a
    ``\boxed{}`` answer token to enable extraction by the API.
    """

    seed = hash(prompt) & 0xFFFFFFFF
    rng = random.Random(seed)

    traces = []
    for i in range(k):
        answer = rng.randint(0, 100)
        trace = (
            f"Trace {i}: thinking about {prompt}. "
            f"The final answer is \\boxed{{{answer}}}."
        )
        traces.append(trace)
    return traces
