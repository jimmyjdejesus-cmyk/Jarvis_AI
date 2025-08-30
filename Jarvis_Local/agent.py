# agent.py
from llama_cpp import Llama
import config
from logger_config import log # <-- IMPORT THE LOGGER

class MetaAgent:
    def __init__(self):
        try:
            self.llm = Llama(
                model_path=config.MODEL_PATH,
                n_ctx=config.N_CTX,
                n_gpu_layers=config.N_GPU_LAYERS,
                verbose=False
            )
            log.info(f"Meta-Agent model loaded successfully from: {config.MODEL_PATH}")
        except Exception as e:
            log.error(f"Failed to load model from path: {config.MODEL_PATH}")
            log.error(f"Error details: {e}")
            self.llm = None

    def invoke(self, prompt, history=None):
        if not self.llm:
            log.warning("Invoke called but model is not loaded.")
            return "Model not loaded. Please check the logs for errors."

        full_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>"

        log.info("Invoking model inference...")
        output = self.llm(
            full_prompt,
            max_tokens=512,
            stop=["<|end|>", "user:"]
        )

        response = output['choices'][0]['text'].strip()
        log.info("Model inference complete.")
        return response