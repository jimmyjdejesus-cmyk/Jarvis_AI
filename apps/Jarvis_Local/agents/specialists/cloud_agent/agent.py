# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# agents/specialists/cloud_agent.py
from Jarvis_Local.agents.base_agent.agent import BaseAgent
from Jarvis_Local.tools.mcp_client import MCPClient

class CloudAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_prompt="You are a powerful cloud-based specialist.")
        try:
            self.mcp_client = MCPClient()
        except Exception as e:
            self.mcp_client = None
            print(f"CloudAgent: MCP client not available - {e}")

    def invoke(self, prompt, history=None):
        if not self.mcp_client or not self.mcp_client.is_configured():
            # Fallback to local model if cloud provider is not configured
            return super().invoke(prompt)

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