"""Default dynamic agent tools backed by a local Ollama LLM."""

from typing import Dict, Any
import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def _call_llm(prompt: str) -> str:
    """Send a prompt to the local Ollama server and return the response."""

    if prompt is None or str(prompt).strip() == "":
        return "(LLM error: prompt is empty or None)"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate", json=payload, timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except (requests.RequestException, ValueError) as exc:  # pragma: no cover - network failure handling
        return f"(LLM error: {exc})"


def planning_tool(objective: str, context: Dict[str, Any]) -> str:
    """Create a step-by-step plan for the objective."""

    prompt = (
        "You are an expert project planner. Break down the objective into concise,"
        " actionable steps.\n"
        f"Objective: {objective}\n"
        "Plan:"
    )
    return _call_llm(prompt)


def research_tool(objective: str, context: Dict[str, Any]) -> str:
    """Perform brief research using the provided plan."""

    plan = context.get("planning", "")
    prompt = (
        "You are a research assistant. Using the plan below, gather information to"
        " address the objective. Respond concisely.\n"
        f"Objective: {objective}\n"
        f"Plan:\n{plan}\n"
        "Research:"
    )
    return _call_llm(prompt)


def analysis_tool(objective: str, context: Dict[str, Any]) -> str:
    """Combine planning and research into a short analysis with next steps."""

    plan = context.get("planning", "")
    research = context.get("research", "")
    prompt = (
        "You are an analyst. Use the plan and research to craft a brief analysis and"
        " recommend next steps.\n"
        f"Objective: {objective}\n"
        f"Plan:\n{plan}\n"
        f"Research:\n{research}\n"
        "Analysis:"
    )
    return _call_llm(prompt)

