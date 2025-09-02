"""
The parent class for all agents.
"""
from llama_cpp import Llama
import settings # Use settings for live configuration
from logger_config import log
from collections import deque
import numpy as np
import os

# Import your confidence utility functions
from agents.utilities.confidence import (
    calculate_average_confidence,
    calculate_lowest_group_confidence,
    calculate_lowest_single_token_confidence
)

class BaseAgent:
    def __init__(self, system_prompt="", llm_instance=None):
        self.system_prompt = system_prompt
        self.llm = llm_instance

        if self.llm:
            log.info(f"Agent {self.__class__.__name__} initialized using a shared model instance.")
        else:
            log.warning(f"Agent {self.__class__.__name__} initialized without a model instance.")

    def invoke(self, prompt, history=None):
        if not self.llm:
            log.warning("Invoke called but model is not loaded.")
            return {"response": "Model not loaded.", "tokens_generated": 0, "group_low_confidence": 0}

        full_prompt = (
            f"<|system|>\n{self.system_prompt}<|end|>\n"
            f"<|user|>\n{prompt}<|end|>\n<|im_start|>assistant\n"
        )

        stream = self.llm.create_completion(
            full_prompt, max_tokens=1024, stop=["<|end|>", "<|im_end|>"],
            temperature=0.1, logprobs=True, stream=True
        )

        final_response_text = ""
        confidences = []
        stopped_early = False
        window_size = 32

        for output in stream:
            token_text = output['choices'][0]['text']
            final_response_text += token_text

            logprobs = output['choices'][0]['logprobs']
            if logprobs and logprobs['token_logprobs']:
                token_conf = -logprobs['token_logprobs'][0]
                confidences.append(token_conf)

                if settings.DEEPCONF_ENABLED and len(confidences) >= window_size:
                    group_conf = np.mean(confidences[-window_size:])
                    if group_conf < settings.CONFIDENCE_THRESHOLD:
                        stopped_early = True
                        break

        if stopped_early:
            final_response_text += "..."

        # --- Correctly calculate stats based ONLY on what was generated ---
        tokens_generated = len(confidences)
        avg_conf = np.mean(confidences) if confidences else 0
        group_low_conf = np.mean(confidences[-window_size:]) if len(confidences) >= window_size else avg_conf
        single_low_conf = min(confidences) if confidences else 0

        log.info(
            "Trace Stats | Tokens: %d | Avg Conf: %.4f | Group Low: %.4f | Single Low: %.4f",
            tokens_generated, avg_conf, group_low_conf, single_low_conf
        )

        # --- The final return dictionary with the typo fixed ---
        return {
            "response": final_response_text,
            "avg_confidence": avg_conf,
            "group_low_confidence": group_low_conf,
            "single_low_confidence": single_low_conf,
            "tokens_generated": tokens_generated
        }