"""Core Meta-Agent logic leveraging a local Llama model."""

from llama_cpp import Llama
import config


class MetaAgent:
    """Wrapper around a local LLM for handling user prompts."""

    def __init__(self):
        """Load the local model specified in the configuration."""
        try:
            self.llm = Llama(
                model_path=config.MODEL_PATH,
                n_ctx=2048,
                n_gpu_layers=-1,
                verbose=False,
            )
            print("Meta-Agent model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.llm = None

    def invoke(self, prompt, history=None):
        """Generate a response from the model.

        Args:
            prompt: User input string.
            history: Optional conversation history.

        Returns:
            str: Model-generated response or error message.
        """
        if not self.llm:
            return "Model not loaded. Please check the model path in config.py."

        full_prompt = f"User: {prompt}\nJ.A.R.V.I.S.:"
        output = self.llm(full_prompt, max_tokens=512, stop=["User:", "\n"])
        response = output['choices'][0]['text'].strip()
        return response
