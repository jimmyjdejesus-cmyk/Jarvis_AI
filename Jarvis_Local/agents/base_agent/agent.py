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

        if self.llm is None:
            try:
                # Correctly load the model ONCE using the live settings
                self.llm = Llama(
                    model_path=settings.ACTIVE_MODEL_PATH,
                    n_ctx=settings.N_CTX,
                    n_gpu_layers=settings.N_GPU_LAYERS,
                    logits_all=True,
                    n_threads=settings.N_THREADS,
                    verbose=False
                )
                log.info(f"New model instance loaded for: {self.__class__.__name__}")
            except Exception as e:
                log.error(f"Failed to load model from path: {settings.ACTIVE_MODEL_PATH}", exc_info=True)
        else:
            log.info(f"Agent {self.__class__.__name__} is sharing an existing model instance.")

    def invoke(self, prompt, history=None):
        if not self.llm:
            log.warning("Invoke called but model is not loaded.")
            return {"response": "Model not loaded. Please check logs.", "tokens_generated": 0, "group_low_confidence": 0}

        full_prompt = (
            f"<|system|>\n{self.system_prompt}<|end|>\n"
            f"<|user|>\n{prompt}<|end|>\n"
            "<|im_start|>assistant\n"
        )

        log.info(f"Invoking model with streaming for {self.__class__.__name__}...")

        # --- Re-enable Streaming for Early Stopping ---
        stream = self.llm.create_completion(
            full_prompt,
            max_tokens=1024,
            stop=["<|end|>", "<|im_end|>"],
            temperature=0.1,
            logprobs=True,
            stream=True
        )

        final_response_text = ""
        full_output_chunks = []
        window_size = 32
        confidences = deque(maxlen=window_size)
        stopped_early = False

        for output in stream:
            full_output_chunks.append(output) # Save each chunk
            token_text = output['choices'][0]['text']
            final_response_text += token_text

            logprobs = output['choices'][0]['logprobs']
            if settings.DEEPCONF_ENABLED and logprobs and logprobs['token_logprobs']:
                confidence = -logprobs['token_logprobs'][0]
                confidences.append(confidence)

                if len(confidences) == window_size:
                    current_group_confidence = np.mean(list(confidences))
                    if current_group_confidence < settings.CONFIDENCE_THRESHOLD:
                        log.warning(f"Stopping early! Group confidence {current_group_confidence:.4f} fell below threshold {settings.CONFIDENCE_THRESHOLD}")
                        stopped_early = True
                        break

        if stopped_early:
            final_response_text += "..."

        # --- Post-Hoc Analysis on the Full (or partial) Stream ---
        # To get usage stats, we need to assemble a final output object
        final_output_object = full_output_chunks[-1] if full_output_chunks else {}
        if 'usage' not in final_output_object:
             final_output_object['usage'] = {'completion_tokens': len(final_response_text.split())}


        tokens_generated = final_output_object.get('usage', {}).get('completion_tokens', 0)

        # Note: For a true stream, you'd calculate confidence on the fly.
        # This post-hoc calculation on the chunks is a simplification.
        avg_conf = np.mean([c for c in confidences]) if confidences else 0
        group_low_conf = min(confidences) if confidences else 0 # Simplified for this example
        single_low_conf = min(confidences) if confidences else 0 # Simplified for this example

        log.info(
            "Trace Stats | Tokens: %d | Avg Conf: %.4f | Group Low Conf: %.4f | Single Low Conf: %.4f",
            tokens_generated, avg_conf, group_low_conf, single_low_conf
        )

        return {
            "response": final_response_text,
            "avg_confidence": avg_conf,
            "group_low_confidence": group_low_conf,
            "single_low_confidence": single_low_conf,
            "tokens_generated": tokens_generated
        }