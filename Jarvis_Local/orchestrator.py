from agents.meta_agent.agent import MetaAgent
from agents.specialists.coding_specialist.agent import CodingAgent
from agents.specialists.research_specialist.agent import ResearchAgent
from agents.specialists.baseline_specialist.agent import BaselineAgent # New baseline agent with minimal prompting
from logger_config import log
from collections import defaultdict
import settings
from llama_cpp import Llama

class Orchestrator:
    def __init__(self):
        log.info("Initializing Orchestrator...")
        llm_instance = None
        try:
            # Get model path and adapt it based on execution context
            model_path = settings.get_active_model_path()
            import os
            
            # Check if we're running from project root or Jarvis_Local
            current_dir = os.getcwd()
            base_dir = os.path.basename(current_dir)
            
            # Special handling for model paths
            if base_dir == "Jarvis_Local":
                # We're already in the Jarvis_Local directory, so strip prefix if it exists
                if model_path.startswith("Jarvis_Local/"):
                    model_path = model_path.replace("Jarvis_Local/", "", 1)
            else:
                # We're in the project root, make sure paths include Jarvis_Local prefix
                if not model_path.startswith("Jarvis_Local/"):
                    if model_path.startswith("./"):
                        model_path = "Jarvis_Local/" + model_path[2:]
                    else:
                        model_path = "Jarvis_Local/" + model_path
                        
            abs_model_path = os.path.abspath(model_path)
            log.info(f"Loading model from: {abs_model_path}")
            log.info(f"Active model name: {settings.ACTIVE_MODEL_NAME}")
            log.info(f"Current working directory: {current_dir}")
            log.info(f"File exists check: {os.path.exists(abs_model_path)}")
            
            # The orchestrator loads the model ONCE.
            llm_instance = Llama(
                model_path=abs_model_path,
                n_ctx=settings.N_CTX,
                n_gpu_layers=settings.N_GPU_LAYERS, # <-- FIX: Corrected parameter name
                logits_all=True,
                n_threads=settings.N_THREADS,
                verbose=settings.VERBOSE
            )
            log.info("Primary model instance loaded successfully by Orchestrator.")
        except Exception:
            llm_instance = None
            log.error("ORCHESTRATOR FAILED TO LOAD MODEL!", exc_info=True)

        # All agents are initialized with the SAME model instance.
        self.meta_agent = MetaAgent(llm_instance=llm_instance)
        self.coding_agent = CodingAgent(llm_instance=llm_instance)
        self.research_agent = ResearchAgent(llm_instance=llm_instance)
        self.baseline_agent = BaselineAgent(llm_instance=llm_instance)
        self.history = []
        log.info("Orchestrator initialization complete.")

    def handle_request(self, user_input):
        """
        Handles a user request by routing, executing, voting, and remediating.
        """
        log.info(f"Orchestrator received request: '{user_input}'")

        # --- 1. Initial Agent Routing ---
        active_agent = self._route_to_initial_agent(user_input)
        if not active_agent or not active_agent.llm:
            return "Error: No active agent or model loaded.", 0, 0.0

        # --- 2. Generate and Vote on Responses ---
        best_response, total_tokens, best_confidence = self._generate_and_vote(active_agent, user_input)

        # --- 3. The CRITIC & REMEDIATION Check ---
        if best_confidence < settings.RELIABILITY_THRESHOLD:
            log.warning(
                f"Initial response confidence ({best_confidence:.4f}) is below "
                f"reliability threshold ({settings.RELIABILITY_THRESHOLD})."
            )
            log.info("ATTEMPTING REMEDIATION with a different specialist.")

            # --- 4. The Remediation Path ---
            remediation_agent = self._get_remediation_agent(active_agent)
            if remediation_agent:
                best_response, total_tokens, best_confidence = self._generate_and_vote(remediation_agent, user_input, is_remediation=True)
            else:
                log.warning("No suitable remediation agent found.")

        self.history.append({"user": user_input, "jarvis": best_response})
        return best_response, total_tokens, best_confidence

    def _route_to_initial_agent(self, user_input):
        """Selects the best initial agent based on keywords or settings."""
        # Force baseline agent if BASELINE_MODE is enabled
        if settings.BASELINE_MODE:
            log.info("BASELINE_MODE active: forcing BaselineAgent.")
            return self.baseline_agent
            
        # Normal routing for optimized mode
        coding_keywords = ["code", "python", "function", "script", "algorithm"]
        research_keywords = ["who", "what is", "when did", "where is", "why do", "search for", "look up"]

        if any(keyword in user_input.lower() for keyword in coding_keywords):
            log.info("Initial route: CodingAgent.")
            return self.coding_agent
        if any(keyword in user_input.lower() for keyword in research_keywords):
            log.info("Initial route: ResearchAgent.")
            return self.research_agent

        log.info("Initial route: MetaAgent.")
        return self.meta_agent

    def _get_remediation_agent(self, failed_agent):
        """Selects a different agent for a remediation attempt."""
        if isinstance(failed_agent, MetaAgent):
            log.info("Remediation: MetaAgent failed, trying ResearchAgent.")
            return self.research_agent
        # Add more remediation rules here in the future
        return None

    def _generate_and_vote(self, agent, user_input, is_remediation=False):
        """Generates multiple candidates and returns the best response based on voting."""
        # If the agent doesn't have a model, return a helpful error message
        if not agent.llm:
            log.warning("Agent has no model loaded - returning fallback response")
            return "Sorry, I couldn't answer that because the AI model isn't loaded properly. Please check the model path in settings.py and make sure it's correct.", 0, 0.0
            
        num_responses = settings.NUM_RESPONSES
        log.info(f"Generating {num_responses} candidates with {agent.__class__.__name__}...")

        responses_data = [agent.invoke(user_input) for _ in range(num_responses)]

        # Debug: Log what responses we got
        for i, res_data in enumerate(responses_data):
            if isinstance(res_data, dict):
                log.info(f"Response {i+1}: tokens={res_data.get('tokens_generated', 0)}, avg_conf={res_data.get('avg_confidence', 0):.4f}, response_length={len(res_data.get('response', ''))}")
            else:
                log.warning(f"Response {i+1}: Invalid response data type: {type(res_data)}")

        vote_tally = defaultdict(float)
        for res_data in responses_data:
            if isinstance(res_data, dict) and "response" in res_data:
                # Use average confidence for voting (higher confidence = better response)
                confidence = res_data.get("avg_confidence", 0)
                response_text = res_data["response"]
                vote_tally[response_text] += confidence
                log.info(f"Voting: '{response_text[:50]}...' gets {confidence:.4f} votes")

        if not vote_tally:
            log.error("No valid responses generated - all responses were invalid!")
            return "Error: No valid responses generated.", 0, 0.0

        best_response = max(vote_tally, key=vote_tally.get)
        best_confidence = vote_tally[best_response]
        total_tokens = sum(r.get('tokens_generated', 0) for r in responses_data if isinstance(r, dict))

        log.info(f"Voting complete. Best response chosen with confidence {best_confidence:.4f}. Total tokens: {total_tokens}")
        log.info(f"Best response preview: '{best_response[:100]}...'")
        return best_response, total_tokens, best_confidence