from agents.base_agent.agent import BaseAgent
from logger_config import log
# This prompt could benefit from abstracting the language to a variable, e.g. `programming_language` 

class CodingAgent(BaseAgent):
    def __init__(self, llm_instance=None):
        super().__init__(llm_instance=llm_instance)
        # Override parents init method
        self.system_prompt = (
            "You are an expert Python programmer. Your task is to provide clean, "
            "efficient, and correct code."
        )
        if self.llm:
            log.info(f"CodingAgent initialized sharing LLM.")
        else:
            log.error("CodingAgent initialized without a shared LLM instance.")

        super().__init__(system_prompt=self.system_prompt, llm_instance=llm_instance)