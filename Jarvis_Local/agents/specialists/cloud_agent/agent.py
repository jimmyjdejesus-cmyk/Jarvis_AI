# agents/specialists/cloud_agent.py
from agents.base_agent.agent import BaseAgent
from tools.mcp_client import MCPClient

class CloudAgent(BaseAgent):
    def __init__(self, llm_instance=None): # Accepts instance but doesn't use it
        super().__init__(system_prompt="You are a powerful cloud-based specialist.", llm_instance=llm_instance)
        self.mcp_client = MCPClient()

    def invoke(self, prompt, history=None):
        # This agent's invoke method calls the cloud instead of a local model
        response, tokens = self.mcp_client.invoke(prompt, self.system_prompt)

        # Return data in the same format as our local agents
        return {
            "response": response,
            "tokens_generated": tokens,
            "avg_confidence": 99.0, # We can assign a high confidence score
            "group_low_confidence": 99.0,
            "single_low_confidence": 99.0
        }