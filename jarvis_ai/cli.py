"""Command-line interface for executing Jarvis missions."""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional, TypeAlias

from jarvis.ecosystem import ExecutiveAgent
from jarvis.mcp.client import McpClient
from jarvis.mcp.protocol import MissionResult

Context: TypeAlias = Dict[str, Any]

def _run_command(args: argparse.Namespace, mcp_client: McpClient) -> None:
    """Execute a mission using the ExecutiveAgent."""
    code_context = None
    if args.code:
        with open(args.code) as f:
            code_context = f.read()

    agent = ExecutiveAgent("cli", mcp_client=mcp_client)
    context: Context = {}
    if code_context:
        context["code"] = code_context
    if args.context:
        context["user_context"] = args.context

    async def run_agent() -> None:
        result = await agent.execute_mission(args.objective, context)
        print(json.dumps(result, indent=2))

    asyncio.run(run_agent())

def main(mcp_client: Optional[McpClient] = None) -> None:
    """Run the Jarvis CLI.

    Parameters
    ----------
    mcp_client : Optional[McpClient], optional
        Pre-initialized MCP client primarily used for testing.

    Returns
    -------
    None
    """
    if mcp_client is None:
        mcp_client = McpClient()

    parser = argparse.ArgumentParser(description="Jarvis AI command line interface")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Execute a mission objective")
    run_parser.add_argument("objective", type=str, help="The main objective for the AI")
    run_parser.add_argument("--code", type=str, help="Path to a code file to be used as context")
    run_parser.add_argument("--context", type=str, help="Additional context for the objective")
    run_parser.set_defaults(func=_run_command)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args, mcp_client)