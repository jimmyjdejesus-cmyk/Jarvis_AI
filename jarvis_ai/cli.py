import argparse
import asyncio
import json

from jarvis.orchestration.orchestrator import MultiAgentOrchestrator

def main(mcp_client=None) -> None:
    if mcp_client is None:
        from jarvis.mcp.client import McpClient
        mcp_client = McpClient()

    parser = argparse.ArgumentParser(description="Run the Jarvis V2 engine.")
    parser.add_argument("objective", type=str, help="The main objective for the AI.")
    parser.add_argument("--code", type=str, help="Path to a code file to be used as context.")
    parser.add_argument("--context", type=str, help="Additional context for the objective.")

    args = parser.parse_args()

    if args.code:
        with open(args.code, "r") as f:
            code_context = f.read()
    else:
        code_context = None

    orchestrator = MultiAgentOrchestrator(mcp_client=mcp_client)

    async def run_orchestrator():
        result = await orchestrator.coordinate_specialists(
            request=args.objective,
            code=code_context,
            user_context=args.context,
        )
        print(json.dumps(result, indent=2))

    asyncio.run(run_orchestrator())

if __name__ == "__main__":
    main()
