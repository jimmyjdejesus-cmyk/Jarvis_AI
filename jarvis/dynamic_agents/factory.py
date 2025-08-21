from typing import Callable, Dict, Any

class DynamicAgent:
    """A simple dynamic agent that orchestrates a set of tools.

    The agent executes each tool in order, passing the objective and
    accumulated context. Results from each tool are stored in the context
    and returned as a single dictionary when the run completes.
    """
    def __init__(self, name: str, tools: Dict[str, Callable[[str, Dict[str, Any]], Any]]):
        self.name = name
        self.tools = tools  # preserve insertion order

    def run(self, objective: str) -> Dict[str, Any]:
        context: Dict[str, Any] = {}
        for name, tool_func in self.tools.items():
            try:
                result = tool_func(objective, context)
            except Exception as exc:
                result = {"error": str(exc), "tool": name, "objective": objective}
            context[name] = result
        return context

def create_dynamic_agent(name: str, tools: Dict[str, Callable[[str, Dict[str, Any]], Any]]) -> DynamicAgent:
    return DynamicAgent(name=name, tools=tools)
