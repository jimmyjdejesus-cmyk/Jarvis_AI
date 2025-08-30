"""Simple orchestrator for routing requests to the meta-agent."""

from agent import MetaAgent


class Orchestrator:
    """Coordinate between user requests and the meta-agent."""

    def __init__(self):
        """Initialize the orchestrator and meta-agent."""
        print("Initializing Orchestrator...")
        self.meta_agent = MetaAgent()
        self.history = []  # Simple list for conversation history

    def handle_request(self, user_input):
        """Process user input and return the agent's response."""
        print(f"Orchestrator received: {user_input}")

        # --- Future Logic Placeholder ---
        # if "code" in user_input.lower():
        #     response = self.coding_agent.invoke(user_input)
        # elif "research" in user_input.lower():
        #     response = self.research_agent.invoke(user_input)
        # else:
        #     response = self.meta_agent.invoke(user_input, self.history)
        # --------------------------------

        response = self.meta_agent.invoke(user_input, self.history)

        # Update history
        self.history.append({"user": user_input, "jarvis": response})
        return response
