# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# agents/specialists/research_specialist/agent.py
from Jarvis_Local.agents.base_agent.agent import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a powerful research specialist focused on accurate historical analysis and logical reasoning.
        
When presented with tricky questions or riddles:
1. First identify key historical facts and context
2. Consider the logical implications of counterfactual scenarios
3. Provide clear explanations of your reasoning process
4. Draw logical conclusions based on evidence

"""
        super().__init__(system_prompt=system_prompt)