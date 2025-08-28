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


def filter_team_outputs(
    context: Dict[str, Any],
    team_outputs: Dict[str, Any] | None,
    team: str,
) -> Dict[str, Any]:
    """Remove keys present in a team's outputs from the shared context.

    Parameters
    ----------
    context:
        Original context dictionary shared among orchestration teams.
    team_outputs:
        Optional mapping of team names to their latest outputs. If ``None`` or
        not a mapping, the context is returned unchanged.
    team:
        Name of the team whose output keys should be excluded.

    Returns
    -------
    Dict[str, Any]
        Shallow copy of ``context`` without keys produced by ``team``.
    """
    output = (
        team_outputs.get(team, {})
        if isinstance(team_outputs, dict)
        else {}
    )
    keys = output.keys() if isinstance(output, dict) else []
    return filter_context(context, keys)