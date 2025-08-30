# orchestrator.py
from agent import MetaAgent
from logger_config import log # <-- IMPORT THE LOGGER

class Orchestrator:
    def __init__(self):
        log.info("Initializing Orchestrator...")
        self.meta_agent = MetaAgent()
        self.history = []
        log.info("Orchestrator initialization complete.")

    def handle_request(self, user_input):
        log.info(f"Orchestrator received request: '{user_input}'")
        response = self.meta_agent.invoke(user_input, self.history)
        self.history.append({"user": user_input, "jarvis": response})
        log.info("Orchestrator processed request and received response.")
        return response