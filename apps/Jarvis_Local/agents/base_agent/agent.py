# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# agents/base_agent/agent.py
"""Base agent class for all agents in the system."""

import ollama
from ... import settings
from ...logger_config import log

class BaseAgent:
    def __init__(self, system_prompt=""):
        self.system_prompt = system_prompt
        # No model loading needed!
        log.info(f"Agent {self.__class__.__name__} initialized.")

    def invoke(self, prompt):
        log.info(f"Invoking {self.__class__.__name__} with model {settings.ACTIVE_MODEL_NAME}...")
        try:
            response = ollama.chat(
                model=settings.ACTIVE_MODEL_NAME,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ]
            )
            response_text = response['message']['content']
            tokens_used = response.get('eval_count', 0)
            # We can assign a default high confidence for now
            return {
                "response": response_text,
                "tokens_generated": tokens_used,
                "group_low_confidence": 10.0,
                "avg_confidence": 10.0,
                "single_low_confidence": 10.0,
            }
        except Exception as e:
            log.error(f"Agent invocation failed: {e}", exc_info=True)
            return {
                "response": f"Error communicating with Ollama: {e}",
                "tokens_generated": 0,
                "group_low_confidence": 0.0,
                "avg_confidence": 0.0,
                "single_low_confidence": 0.0,
            }