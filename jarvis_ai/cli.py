"""Command-line interface for executing Jarvis missions."""

import argparse
import asyncio
import json

from jarvis.ecosystem import ExecutiveAgent


def main(mcp_client=None) -> dict | None:
    """Run the Jarvis CLI.

    Parameters
    ----------
    mcp_client : optional
        Pre-initialized MCP client primarily used for testing.

    Returns
    -------
    dict | None
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

    if args.code:
        with open(args.code, "r") as f:
            code_context = f.read()
    else:
        code_context = None

    context = {}
    if code_context is not None:
        context["code"] = code_context
    if args.context:
        context["user_context"] = args.context

    meta_agent = ExecutiveAgent("cli_meta", mcp_client=mcp_client)

    async def run_meta_agent() -> dict | None:
        """Execute the mission and print results and execution graph.

        Returns
        -------
        dict | None
            Mission result if execution succeeds; otherwise ``None`` when
            planning or execution fails.
        """
        try:
            plan = meta_agent.manage_directive(args.objective, context)
        except Exception as exc:  # pragma: no cover - defensive programming
            print(f"Mission planning failed: {exc}")
            return

        if not plan.get("success", True):
            print("Mission planning failed:")
            print(plan.get("error", "Unknown error"))
            return

        try:
            result = await meta_agent.execute_mission(args.objective, context)
        except Exception as exc:  # pragma: no cover - defensive programming
            print(f"Mission execution failed: {exc}")
            return

        if not result.get("success", True):
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
