# tools/mcp_client.py
from .key_manager import load_api_key
from openai import OpenAI
from ..logger_config import log

class MCPClient:
    def __init__(self):
        self.api_key = load_api_key()
        if not self.api_key:
            log.warning("MCP Initialization without API key - OpenAI features will be unavailable.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def is_configured(self):
        """Check if the client is ready to make calls"""
        return self.client is not None

    def invoke(self, prompt, system_prompt="You are a helpful assistant.", model="gpt-4o"):
        if not self.is_configured():
            return "error: OpenAI API key not configured, please add it.", 0
        
        log.info(f"MCP Client: Invoking cloud model '{model}'...")
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            response = completion.choices[0].message.content
            tokens = completion.usage.total_tokens
            log.info(f"MCP Client: Received response. Tokens used: {tokens}")
            return response, tokens
        except Exception as e:
            log.error("MCP Client failed to get response from cloud model.", exc_info=True)
            return f"Error: Could not contact cloud API. {e}", 0