# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from logger_config import log
from agents.meta_agent.agent import MetaAgent
from agents.specialists.coding_specialist.agent import CodingAgent
from agents.specialists.research_specialist.agent import ResearchAgent


class Orchestrator:
    """A lightweight orchestrator for the AdaptiveMind Local runtime.

    This initializes the main agent instances and exposes a few
    convenience entry points used by the UI and test harness.
    """
    def __init__(self):
        log.info("Initializing Orchestrator and agents...")

        # --- Initialize agents ---
        self.meta_agent = MetaAgent()
        self.coding_agent = CodingAgent()
        self.research_agent = ResearchAgent()
        # Additional agents can be constructed as needed for runtime
        self.history = []
        log.info("Orchestrator initialization complete.")

    def handle_request(self, request: str):
        # Minimal demonstration: call the meta agent synchronously and return a result 
        # that matches the expected (text, tokens, confidence) tuple used by the UI.
        res = self.meta_agent.invoke(request)
        text = res.get("response", "")
        tokens = res.get("tokens_generated", 0)
        confidence = res.get("avg_confidence", 0.0)
        return text, tokens, confidence
# In orchestrator.py __init__
from logger_config import log
from agents.meta_agent.agent import MetaAgent
from agents.specialists.coding_specialist.agent import CodingAgent
from agents.specialists.research_specialist.agent import ResearchAgent
# Import other agents as needed

def __init__(self):
    log.info("Initializing Orchestrator and agents...")
    # No more model loading! It's handled by Ollama.

    # ---Initialize agents ---
    self.meta_agent = MetaAgent()
    self.coding_agent = CodingAgent()
    self.research_agent = ResearchAgent()
    # --- Initialize other agents as needed
    self.history = []
    log.info("Orchestrator initialization complete.")