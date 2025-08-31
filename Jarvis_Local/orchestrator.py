# orchestrator.py
from agent import MetaAgent
from specialist.specialist_agent import CodingAgent # <-- IMPORT THE NEW AGENT
from logger_config import log

class Orchestrator:
    def __init__(self):
        log.info("Initializing Orchestrator...")
        # The MetaAgent loads the model into memory
        self.meta_agent = MetaAgent()
        # The CodingAgent SHARES the loaded model instance to save resources
        self.coding_agent = CodingAgent(shared_llm_instance=self.meta_agent.llm)

        self.history = []
        log.info("Orchestrator initialization complete with all agents.")

    def handle_request(self, user_input):
        log.info(f"Orchestrator received request: '{user_input}'")

        # --- This is the new routing logic ---
        # A simple keyword-based router.
        coding_keywords = ["code", "python", "function", "script", "algorithm"]
        if any(keyword in user_input.lower() for keyword in coding_keywords):
            log.info("Request routed to CodingAgent.")
            response = self.coding_agent.invoke(user_input, self.history)
        else:
            log.info("Request routed to MetaAgent.")
            response = self.meta_agent.invoke(user_input, self.history)

        self.history.append({"user": user_input, "jarvis": response})
        log.info("Orchestrator processed request and received response.")
        return response