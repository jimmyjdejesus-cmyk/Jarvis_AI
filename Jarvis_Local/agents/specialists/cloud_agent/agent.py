# agents/specialists/cloud_agent.py
from agents.base_agent.agent import BaseAgent
from tools.mcp_client import MCPClient

class CloudAgent(BaseAgent):
    def __init__(self, llm_instance=None):
        super().__init__(system_prompt="You are a powerful cloud-based specialist.", llm_instance=llm_instance)
        try:
            self.mcp_client = MCPClient()
        except Exception as e:
            self.mcp_client = None
            print(f"CloudAgent: MCP client not available - {e}")

    def invoke(self, prompt, history=None):
        if not self.mcp_client or not self.mcp_client.is_configured():
            # Fallback to local model if OpenAI is not configured
            if self.llm:
                return super().invoke(prompt, history)
            else:
                return {
                    "response": "Cloud service unavailable and no local model configured.",
                    "tokens_generated": 0,
                    "avg_confidence": 0.0,
                    "group_low_confidence": 0.0,
                    "single_low_confidence": 0.0
                }

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