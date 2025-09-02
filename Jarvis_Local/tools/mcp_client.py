# tools/mcp_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from logger_config import log

load_dotenv() # Load variables from .env file

class MCPClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            log.error("OPENAI_API_KEY not found in .env file.")
            raise ValueError("API key not configured.")
        self.client = OpenAI(api_key=api_key)

    def invoke(self, prompt, system_prompt="You are a helpful assistant.", model="gpt-4o"):
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