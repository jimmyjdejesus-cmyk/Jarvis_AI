# specialist_agent.py
from llama_cpp import Llama
import config
from logger_config import log
import numpy as np

class CodingAgent:
    def __init__(self, shared_llm_instance):
        # This agent USES THE SAME an already loaded model
        # to save memory.
        self.llm = shared_llm_instance
        log.info("CodingAgent has been initialized and is sharing the core LLM.")

    def _calculate_average_confidence(self, output):
        """Calculates the average token confidence"""
        try:
            # Extract the list of log probabilites for each token in the generated sequence
            token_logprobs = output['choices'][0]['logprobs']['token_logprobs']
    
            # Confidence is the negative log probability. Use numpy for stable average
            # Skip the first token, often has no log prob (Start of sequence token)
            if len(token_logprobs) > 1:
                avg_confidence = -np.mean(token_logprobs[1:])
                return avg_confidence
            return 0.0
        except (KeyError, IndexError, TypeError):
            # Handle cases where logprobs might be missing or empty
            log.warning("Logs empty or missing.")
            return 0.0

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
            max_tokens=1024,
            stop=["<|end|>", "user:"],
            temperature=0.1,
            logprobs=True
        )

        response = output['choices'][0]['text'].strip()

        avg_confidence = self._calculate_average_confidence(output)
        log.info(f"Average token confidence: {avg_confidence:.4f}")

        log.info("CodingAgent inference complete.")
        return response