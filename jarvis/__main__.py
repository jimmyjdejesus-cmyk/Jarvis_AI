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
    parser = argparse.ArgumentParser(description="Run Jarvis locally (CLI or --gui)")
    parser.add_argument("objective", type=str, nargs="?", help="Objective (CLI mode)")
    parser.add_argument("--gui", action="store_true", help="Launch the desktop UI")
    
    args = parser.parse_args()
    if args.gui:
        try:
            from .ui import JarvisChatUI
        except ModuleNotFoundError:
            print("Tkinter not available. Install Tkinter or run CLI without --gui.")
            return
        ui = JarvisChatUI()
        ui.start()
        return

    if not args.objective:
        parser.error("objective is required unless --gui is used")

    agent = build_default_agent()
    result = agent.run(args.objective)
    for k,v in result.items():
        print(f"===== {k.upper()} =====\n{v}\n")

if __name__ == "__main__":
    main()
