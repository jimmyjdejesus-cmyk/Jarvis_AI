"""Default dynamic agent tools with optional Ollama LLM support."""

import os
import requests
from typing import Dict, Any

# Ollama configuration (optional)
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = 30
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"


def _call_llm(prompt: str) -> str:
    """Send a prompt to the local Ollama server and return the response."""
    if prompt is None or str(prompt).strip() == "":
        return "(LLM error: prompt is empty or None)"
    
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate", 
            json=payload, 
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        return response.json().get("response", "(No response from LLM)")
    except Exception as exc:
        return f"(LLM error: {exc})"


def planning_tool(objective: str, context: Dict[str, Any]) -> str:
    """Create a step-by-step plan for the objective.
    
    Uses Ollama LLM if available, otherwise falls back to simple logic.
    """
    if USE_OLLAMA:
        prompt = (
            "You are an expert project planner. Break down the objective into concise,"
            " actionable steps.\n"
            f"Objective: {objective}\n"
            "Plan:"
        )
        return _call_llm(prompt)
    else:
        # Simple fallback logic
        words = [w for w in objective.split() if w]
        steps = [f"Step {i+1}: Address '{w}'" for i, w in enumerate(words[:6])]
        return "\n".join(steps) if steps else "No plan generated."


def research_tool(objective: str, context: Dict[str, Any]) -> str:
    """Perform research using the provided plan.
    
    Uses Ollama LLM if available, otherwise provides simple output.
    """
    plan = context.get("planning", "(no plan available)")
    
    if USE_OLLAMA:
        prompt = (
            "You are a research assistant. Using the plan below, gather information to"
            " address the objective. Respond concisely.\n"
            f"Objective: {objective}\n"
            f"Plan:\n{plan}\n"
            "Research:"
        )
        return _call_llm(prompt)
    else:
        # Simple fallback
        return (f"Performed quick desk-research on: '{objective}'.\n"
                f"Used plan:\n{plan}\n\n(Replace with web/RAG tools.)")


def analysis_tool(objective: str, context: Dict[str, Any]) -> str:
    """Combine planning and research into analysis with next steps.
    
    Uses Ollama LLM if available, otherwise provides synthesis.
    """
    plan = context.get("planning", "(no plan)")
    research = context.get("research", "(no research)")
    
    if USE_OLLAMA:
        prompt = (
            "You are an analyst. Use the plan and research to craft a brief analysis and"
            " recommend next steps.\n"
            f"Objective: {objective}\n"
            f"Plan:\n{plan}\n"
            f"Research:\n{research}\n"
            "Analysis:"
        )
        return _call_llm(prompt)
    else:
        # Simple fallback
        return ("Synthesis/Analysis: combining plan and research.\n\n"
                f"PLAN:\n{plan}\n\nRESEARCH:\n{research}\n\n(Replace with tests/evals.)")
