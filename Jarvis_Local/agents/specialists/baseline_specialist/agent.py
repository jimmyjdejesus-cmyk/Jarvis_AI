# agents/specialists/baseline_specialist/agent.py
from agents.base_agent.agent import BaseAgent

class BaselineAgent(BaseAgent):
    def __init__(self, llm_instance=None):
        # Minimal system prompt - no chain of thought, no detailed instructions
        system_prompt = "You are a helpful AI assistant. Answer questions directly and concisely."
        super().__init__(system_prompt=system_prompt, llm_instance=llm_instance)
