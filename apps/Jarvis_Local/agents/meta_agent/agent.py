# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from Jarvis_Local.agents.base_agent.agent import BaseAgent

class MetaAgent(BaseAgent):
    def __init__(self):
        system_prompt = "You are J.A.R.V.I.S., a highly capable and intelligent AI assistant."
        super().__init__(system_prompt=system_prompt)