"""Utility helpers for manipulating team context dictionaries."""
from typing import Dict, Iterable, Any


def filter_context(
    context: Dict[str, Any], exclude: Iterable[str]
) -> Dict[str, Any]:
    """Return a copy of ``context`` excluding any keys found in ``exclude``.

    Parameters
    ----------
    context:
        Original context dictionary passed between orchestration teams.
    exclude:
        Iterable of keys that should be removed from the returned context.

    Returns
    -------
    Dict[str, Any]
        Shallow copy of ``context`` without the excluded keys.
    """
    exclude_set = set(exclude)
    return {k: v for k, v in context.items() if k not in exclude_set}
