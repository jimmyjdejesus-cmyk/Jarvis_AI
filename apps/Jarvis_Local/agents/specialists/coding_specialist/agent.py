# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from Jarvis_Local.agents.base_agent.agent import BaseAgent
from Jarvis_Local.logger_config import log
# This prompt could benefit from abstracting the language to a variable, e.g. `programming_language` 

class CodingAgent(BaseAgent):
    def __init__(self):
        # Minimal rewrite: call BaseAgent once with the prompt
        system_prompt = (
            "You are an expert Python programmer. Your task is to provide clean, "
            "efficient, and correct code."
        )
        super().__init__(system_prompt=system_prompt)
        log.info(f"CodingAgent initialized.")