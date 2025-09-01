"""
The parent class for all agents.
"""

from llama_cpp import Llama
import config
from logger_config import log
from collections import deque
import numpy as np

from agents.utilities.confidence import calculate_average_confidence, calculate_lowest_group_confidence, calculate_lowest_single_token_confidence


class BaseAgent:
    def __init__(self, system_prompt=""):
        self.system_prompt = system_prompt
        self.llm = None  # Initialize llm as None
        try:
            self.llm = Llama(
                model_path=config.MODEL_PATH,
                n_ctx=config.N_CTX,
                n_gpu_layers=config.N_GPU_LAYERS,
                verbose=False,
                logits_all=True,  # Enable logits for logprobs support
                n_threads=config.N_THREADS  # Use the configured number of threads
            )
            log.info(
                "Model loaded for agent with persona: %s",
                self.__class__.__name__,
            )
        except Exception:
            log.error("Failed to load model", exc_info=True)

    
    def invoke(self, prompt, history=None):
        if not self.llm:
            log.warning("Invoke called but model is not loaded.")
            return "Model not loaded. Please check the logs for errors."

        full_prompt = (
            f"<|system|>\n{self.system_prompt}<|end|>\n"
            f"<|user|>\n{prompt}<|end|>\n"
            "<|im_start|>assistant\n"
        )

        log.info(f"Invoking model with streaming for {self.__class__.__name__}...")

        # --- Enable Streaming ---
        output = self.llm(
            full_prompt,
            max_tokens=1024,
            stop=["<|end|>", "<|im_end|>"],
            temperature=0.1,
            logprobs=True,
        )

        response = output['choices'][0]['text'].strip     
        # --- Post-processing confidence metrics ---
        tokens_generated = output.get('usage', {}).get('completion_tokens', 0)

        avg_conf = calculate_average_confidence(output)
        group_low_conf = calculate_lowest_group_confidence(output)
        single_low_conf = calculate_lowest_single_token_confidence(output)
        log.info(
            "Trace Stats | Tokens: %d | Avg Conf: %.4f | Group Low Conf: %.4f | Single Low Conf: %.4f",
            tokens_generated, avg_conf, group_low_conf, single_low_conf
        )
        log.info("Model inference complete.")
        
        # Instead of returning final response
        # Return a dictionary with all the data
        return {
            "response": response,
            "avg_confidence": avg_conf,
            "group_low_confidence": group_low_conf,
            "single_low_confidence": single_low_conf,
            "tokens_generated": tokens_generated
        }
