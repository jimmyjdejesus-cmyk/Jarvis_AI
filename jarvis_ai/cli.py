"""Command-line interface for executing Jarvis missions."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any, TYPE_CHECKING, TypeAlias, TypedDict

from jarvis.ecosystem import ExecutiveAgent

if TYPE_CHECKING:  # pragma: no cover - typing only
    from jarvis.mcp.client import McpClient


Context: TypeAlias = dict[str, Any]


class MissionPlan(TypedDict, total=False):
    """Structure describing a planned mission."""

    success: bool
    graph: dict[str, Any]
    error: str


class MissionResult(TypedDict, total=False):
    """Structure containing mission execution results."""

    success: bool
    results: list[Any]
    error: str


def _build_context(
    code_path: str | None, user_context: str | None
) -> Context:
    """Construct mission context from optional code and text.

    Parameters
    ----------
    code_path : str | None
        Path to a file whose contents should be added under the ``code`` key.
    user_context : str | None
        Additional context string associated with the ``user_context`` key.

    Returns
    -------
    Context
        Dictionary populated with any provided values.
    """

    context: Context = {}
    if code_path:
        with open(code_path, "r") as f:
            context["code"] = f.read()
    if user_context:
        context["user_context"] = user_context
    return context


def main(mcp_client: McpClient | None = None) -> MissionResult | None:
    """Run the Jarvis CLI.

    Parameters
    ----------
    mcp_client : McpClient | None, optional
        Pre-initialized MCP client primarily used for testing.

    Returns
    -------
    MissionResult | None
        Mission result dictionary if execution succeeds; otherwise ``None``.
    """
    if mcp_client is None:
        from jarvis.mcp.client import McpClient
        mcp_client = McpClient()

    parser = argparse.ArgumentParser(description="Run the Jarvis V2 engine.")
    parser.add_argument(
        "objective",
        type=str,
        help="The main objective for the AI.",
    )
    parser.add_argument(
        "--code",
        type=str,
        help="Path to a code file to be used as context.",
    )
    parser.add_argument(
        "--context",
        type=str,
        help="Additional context for the objective.",
    )

    args = parser.parse_args()

    context: Context = _build_context(args.code, args.context)

    meta_agent: ExecutiveAgent = ExecutiveAgent(
        "cli_meta", mcp_client=mcp_client
    )

    async def run_meta_agent() -> MissionResult | None:
        """Execute the mission and print results and execution graph.

        Returns
        -------
        MissionResult | None
            Mission result containing ``success`` and ``results`` keys when
            execution succeeds. ``None`` is returned if planning or execution
            fails.
        """
        try:
            plan: MissionPlan = meta_agent.manage_directive(
                args.objective, context
            )
        except Exception as exc:  # pragma: no cover - defensive programming
            print(f"Mission planning failed: {exc}")
            return

        if not plan.get("success", False):
            print("Mission planning failed:")
            print(plan.get("error", "Unknown error"))
            return

        try:
            result: MissionResult = await meta_agent.execute_mission(
                args.objective, context
            )
        except Exception as exc:  # pragma: no cover - defensive programming
            print(f"Mission execution failed: {exc}")
            return

        if not result.get("success", False):
            print("Mission execution failed:")
            print(result.get("error", "Unknown error"))
            return

        print("Mission Results:")
        print(json.dumps(result, indent=2))
        if plan.get("graph"):
            print("Execution Graph:")
            print(json.dumps(plan["graph"], indent=2))

        return result

    mission_result = asyncio.run(run_meta_agent())
    return mission_result


if __name__ == "__main__":
    main()
