# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# agents/specialists/baseline_specialist/agent.py
from Jarvis_Local.agents.base_agent.agent import BaseAgent

class BaselineAgent(BaseAgent):
    def __init__(self):
        # Minimal system prompt - no chain of thought, no detailed instructions
        system_prompt = "You are a helpful AI assistant."
        super().__init__(system_prompt=system_prompt)
