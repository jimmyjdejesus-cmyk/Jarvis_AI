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
        log.info(f"Orchestrator received request: '{user_input}'")
        active_agent = None
        
        # -- Keywords to invoke a specialist --
        coding_keywords = ["code", "python", "function", "script", "algorithm"]


        if any(keyword in user_input.lower() for keyword in coding_keywords):
            log.info("Request routed to CodingAgent.")
            active_agent = self.coding_agent
        else:
            log.info("Request routed to MetaAgent.")
            active_agent = self.meta_agent
        
        # -- Generate multiple responses -- 
        responses_data = []
        for i in range(settings.NUM_RESPONSES):
            log.info(f"Generating candidate {i+1}/{settings.NUM_RESPONSES}...")
            responses_data.append(active_agent.invoke(user_input))

        # -- Perform Confidence-Weighted Voting --
        log.info("All candidates generated. Performing confidence-weighted voting...")
        vote_tally = defaultdict(float)
        for res_data in responses_data:
            # We use the group_low_confidence as our voting weight
            # A higher score means a more confident vote
            if isinstance(res_data, dict) and "response" in res_data and "group_low_confidence" in res_data:
                vote_tally[res_data["response"]] += res_data["group_low_confidence"]
            else:
                log.warning(f"Orchestrator Ignoring invalid response data: {res_data}")
        
        # Find the response with the highest total confidence score
        if not vote_tally:
            return "No valid responses generated for voting."
        else:
            best_response = max(vote_tally, key=vote_tally.get)
        
        # Aggregate tokens generated
        total_tokens = sum(r['tokens_generated'] for r in responses_data)
        log.info(f"Voting Complete. Best response chosen. Total tokens generated for this request: {total_tokens}")
        
        self.history.append({"user": user_input, "jarvis": best_response})

        return best_response, total_tokens