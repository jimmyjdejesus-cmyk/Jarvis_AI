# specialist_agent.py
from llama_cpp import Llama
import config
from logger_config import log

class CodingAgent:
    def __init__(self, shared_llm_instance):
        # This agent USES THE SAME an already loaded model
        # to save memory.
        self.llm = shared_llm_instance
        log.info("CodingAgent has been initialized and is sharing the core LLM.")

    def invoke(self, prompt, history=None):
        if not self.llm:
            log.warning("CodingAgent invoked but model is not loaded.")
            return "Model not loaded. Please check the console for errors."

        # This specialized prompt makes the model act like a coding expert.
        full_prompt = (
            "<|system|>\nYou are an expert Python programmer. Your task is to provide clean, "
            "efficient, and correct code. Always wrap your code in ```python ... ``` blocks. "
            "Provide a brief explanation of your code after the block.<|end|>\n"
            f"<|user|>\n{prompt}<|end|>\n<|assistant|>"
        )

        log.info("CodingAgent invoking model inference...")
        output = self.llm(
            full_prompt,
            max_tokens=1024, # Give it more room for code
            stop=["<|end|>", "user:"],
            temperature=0.1
        )

        response = output['choices'][0]['text'].strip()
        log.info("CodingAgent inference complete.")
        return response