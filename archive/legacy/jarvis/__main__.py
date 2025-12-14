import argparse
from .dynamic_agents import create_dynamic_agent, default_tools

def build_default_agent():
    tools = {
        "planning": default_tools.planning_tool,
        "research": default_tools.research_tool,
        "analysis": default_tools.analysis_tool,
    }
    return create_dynamic_agent("default_agent", tools)

def main() -> None:
    parser = argparse.ArgumentParser(description="Run Jarvis locally (CLI)")
    parser.add_argument("objective", type=str, help="Objective (CLI mode)")
    args = parser.parse_args()

    agent = build_default_agent()
    result = agent.run(args.objective)
    for k,v in result.items():
        print(f"===== {k.upper()} =====\n{v}\n")

if __name__ == "__main__":
    main()
