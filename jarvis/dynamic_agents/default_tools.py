from typing import Dict, Any

def planning_tool(objective: str, context: Dict[str, Any]) -> str:
    words = [w for w in objective.split() if w]
    steps = [f"Step {i+1}: Address '{w}'" for i, w in enumerate(words[:6])]  # cap for readability
    return "\n".join(steps) if steps else "No plan generated."

def research_tool(objective: str, context: Dict[str, Any]) -> str:
    plan = context.get("planning", "(no plan available)")
    return (f"Performed quick desk-research on: '{objective}'.\n"
            f"Used plan:\n{plan}\n\n(Replace with web/RAG tools.)")

def analysis_tool(objective: str, context: Dict[str, Any]) -> str:
    plan = context.get("planning", "(no plan)")
    research = context.get("research", "(no research)")
    return ("Synthesis/Analysis: combining plan and research.\n\n"
            f"PLAN:\n{plan}\n\nRESEARCH:\n{research}\n\n(Replace with tests/evals.)")
