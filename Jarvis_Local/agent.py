"""Core meta-agent logic for running a local LLM."""

from llama_cpp import Llama
import config


class MetaAgent:
    """Wrapper around a local LLM model."""

    def __init__(self):
        """Load the model specified in :mod:`config`."""
        try:
            self.llm = Llama(
                model_path=config.MODEL_PATH,
                n_ctx=2048,  # Context window
                n_gpu_layers=-1,  # Offload all layers to GPU
                verbose=False,
            )
            print("Meta-Agent model loaded successfully.")
        except Exception as e:  # noqa: BLE001 - broad for logging
            print(f"Error loading model: {e}")
            self.llm = None

    def invoke(self, prompt, history=None):
        """Generate a response from the model.

        Parameters
        ----------
        prompt: str
            User prompt to send to the model.
        history: list | None
            Conversation history for future use.
        """
        if not self.llm:
            return "Model not loaded. Please check the model path in config.py."

        full_prompt = f"User: {prompt}\nJ.A.R.V.I.S.:"
        output = self.llm(full_prompt, max_tokens=512, stop=["User:", "\n"])
        response = output['choices'][0]['text'].strip()
        return response
