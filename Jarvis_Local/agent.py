# agent.py
from llama_cpp import Llama
import config
from logger_config import log # <-- IMPORT THE LOGGER\]
import numpy as np
class MetaAgent:
    def __init__(self):
        try:
            self.llm = Llama(
                model_path=config.MODEL_PATH,
                n_ctx=config.N_CTX,
                n_gpu_layers=config.N_GPU_LAYERS,
                verbose=False,
                logits_all=True  # Enable logits for logprobs support
            )
            log.info(f"Meta-Agent model loaded successfully from: "
                     f"{config.MODEL_PATH}")
        except Exception as e:
            log.error(f"Failed to load model from path: {config.MODEL_PATH}")
            log.error(f"Error details: {e}")
            self.llm = None

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
            log.warning("Invoke called but model is not loaded.")
            return "Model not loaded. Please check the logs for errors."

        full_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>"

        log.info("Invoking model inference...")
        output = self.llm(
            full_prompt,
            max_tokens=512,
            stop=["<|end|>", "user:"],
            temperature=0.1,
            logprobs=True
        )
    
        log.info(f"LLM output structure: {output}")

        response = output['choices'][0]['text'].strip()
        avg_confidence = self._calculate_average_confidence(output)
        log.info(f"Average token confidence: {avg_confidence:.4f}")

        log.info("Model inference complete.")
        return response