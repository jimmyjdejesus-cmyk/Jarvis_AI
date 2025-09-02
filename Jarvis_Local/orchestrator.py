from agents.meta_agent.agent import MetaAgent
from agents.specialists.coding_specialist.agent import CodingAgent
from logger_config import log
from collections import defaultdict
import settings
from llama_cpp import Llama


class Orchestrator:
    def __init__(self):
        log.info("Initializing Orchestrator...")
        llm_instance = None
        try:
           llm_instance = Llama(
               model_path=settings.get_active_model_path(),
               n_ctx=settings.N_CTX,
               n_gpu_layers=settings.N_GPU_LAYERS,
               logits_all=True,
               n_threads=settings.N_THREADS,
               verbose=settings.VERBOSE
           )
           log.info(f"Primary Model loaded successfully by Orchestrator.")
        except Exception:
           llm_instance = None
           log.error("Orchestrator failed to load model!", exc_info=True)

        self.meta_agent = MetaAgent(llm_instance=llm_instance)
        self.coding_agent = CodingAgent(llm_instance=llm_instance)
        self.history = []
        log.info("Orchestrator initialization complete, agents sharing 1 model")

    def handle_request(self, user_input):  # Add parameter with default
        log.info(f"Orchestrator received request: '{user_input}'. Generating {settings.NUM_RESPONSES} candidates for voting.")

        # --- 1. Agent Routing (same as before) ---
        active_agent = None
        coding_keywords = ["code", "python", "function", "script", "algorithm"]
        if any(keyword in user_input.lower() for keyword in coding_keywords):
            log.info("Request routed to CodingAgent.")
            active_agent = self.coding_agent
        else:
            log.info("Request routed to MetaAgent.")
            active_agent = self.meta_agent

        if not active_agent or not active_agent.llm:
            return "Error: No active agent or model loaded.", 0

        # --- 2. Generate Multiple Candidate Responses ---
        responses_data = []
        for i in range(settings.NUM_RESPONSES):
            log.info(f"Generating candidate {i+1}/{settings.NUM_RESPONSES}...")
            responses_data.append(active_agent.invoke(user_input))

        # --- 3. Perform Confidence-Weighted Voting ---
        log.info("All candidates generated. Performing confidence-weighted voting...")
        vote_tally = defaultdict(float)

        for res_data in responses_data:
            # Ensure the response was valid before tallying
            if isinstance(res_data, dict) and "response" in res_data:
                # We use 'group_low_confidence' as our voting weight.
                # A higher score means a more confident vote.
                vote_tally[res_data["response"]] += res_data.get("group_low_confidence", 0)

        # --- 4. Select the Best Response ---
        if not vote_tally:
            best_response = "Error: No valid responses were generated for voting."
        else:
            # Find the response with the highest total confidence score
            best_response = max(vote_tally, key=vote_tally.get)
            log.info(f"Voting complete. Selected best response with total confidence of {vote_tally[best_response]:.4f}")

        # --- 5. Aggregate Final Stats ---
        total_tokens = sum(r.get('tokens_generated', 0) for r in responses_data if isinstance(r, dict))

        self.history.append({"user": user_input, "jarvis": best_response})

        return best_response, total_tokens