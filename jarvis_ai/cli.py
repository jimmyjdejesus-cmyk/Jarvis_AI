import argparse
import asyncio
import json
from typing import Optional, Dict, Any

def _run_command(args, mcp_client) -> None:
    """Execute a mission using the ExecutiveAgent."""
    from jarvis.ecosystem import ExecutiveAgent
    if args.code:
        with open(args.code, "r") as f:
            code_context = f.read()
    else:
        code_context = None

    agent = ExecutiveAgent("cli", mcp_client=mcp_client)
    context: Dict[str, Any] = {}
    if code_context:
        context["code"] = code_context
    if args.context:
        context["user_context"] = args.context

    async def run_agent() -> None:
        result = await agent.execute_mission(args.objective, context)
        print(json.dumps(result, indent=2))

    asyncio.run(run_agent())

def main(mcp_client: Optional[object] = None) -> None:
    if mcp_client is None:
        from jarvis.mcp.client import McpClient
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

if __name__ == "__main__":
    main()
