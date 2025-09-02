from agents.base_agent.agent import BaseAgent

class MetaAgent(BaseAgent):
    def __init__(self, llm_instance=None):
        system_prompt = "You are J.A.R.V.I.S., a highly capable and intelligent AI assistant."
        super().__init__(system_prompt=system_prompt, llm_instance=llm_instance)