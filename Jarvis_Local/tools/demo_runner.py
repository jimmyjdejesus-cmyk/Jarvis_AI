# tools/demo_runner.py
import settings
from orchestrator import Orchestrator
from logger_config import log
import time

DEMO_PROMPT = "If Napoleon had won the Battle of Waterloo, what would the 16th President's grandfather's name have been?"

def run_demo(update_callback):
    """
    Runs the A/B demo and uses a callback to post the final results.
    """
    try:
        update_callback("--- STARTING NAPOLEON RIDDLE DEMO ---")
        update_callback("🤔 Analyzing: 'If Napoleon had won the Battle of Waterloo, what would the 16th President's grandfather's name have been?'")
        update_callback("💭 This is a classic logic puzzle requiring historical and hypothetical reasoning...")

        # --- Run 1: Baseline ---
        update_callback("\n[1/2] 🏃 BASELINE MODE - Minimal agent, no remediation")
        update_callback("📊 Settings: 1 response, confidence threshold disabled, no deep analysis")
        settings.BASELINE_MODE = True     # Force use of the BaselineAgent with minimal prompt
        settings.RELIABILITY_THRESHOLD = 0.2 # Effectively disable remediation
        settings.DEEPCONF_ENABLED = False
        settings.CONFIDENCE_THRESHOLD = 0.0 # Disable confidence filtering
        settings.NUM_RESPONSES = 1  # Single response for baseline
        settings.MAX_TOKENS = 750  # Limit token generation to avoid excessive responses
        
        update_callback("🔄 Initializing orchestrator with baseline settings...")
        orchestrator = Orchestrator()
        
        update_callback("🎯 Routing to initial agent for riddle analysis...")
        baseline_response, baseline_tokens, baseline_confidence = orchestrator.handle_request(DEMO_PROMPT)
        
        update_callback(f"📈 Baseline result: {baseline_tokens} tokens used, confidence: {baseline_confidence:.4f}")
        update_callback("💡 Baseline thinking complete - moving to optimized mode...")

        # --- Run 2: Optimized J.A.R.V.I.S. ---
        update_callback("\n[2/2] 🚀 OPTIMIZED J.A.R.V.I.S. FRAMEWORK - Multi-agent with remediation")
        update_callback("📊 Settings: Multi-response voting, confidence analysis enabled, remediation active")
        settings.BASELINE_MODE = False    # Disable baseline mode for full J.A.R.V.I.S. framework
        settings.RELIABILITY_THRESHOLD = 0.7 # Tuned to trigger remediation when needed
        settings.DEEPCONF_ENABLED = True
        settings.CONFIDENCE_THRESHOLD = 0.2 # Enable confidence filtering but not too aggressive
        settings.NUM_RESPONSES = 2 # Multiple responses for optimized mode
        settings.MAX_TOKENS = 750  # Limit token generation to avoid excessive responses
        
        update_callback("🔄 Re-initializing orchestrator with optimized settings...")
        optimized_orchestrator = Orchestrator()
        
        update_callback("🎯 Starting multi-agent analysis of Napoleon riddle...")
        update_callback("🧠 MetaAgent analyzing riddle structure and routing decision...")
        update_callback("🔍 ResearchAgent gathering historical context and logical reasoning...")
        update_callback("⚖️ Confidence analysis and voting system activated...")
        
        optimized_response, optimized_tokens, optimized_confidence = optimized_orchestrator.handle_request(DEMO_PROMPT)
        
        update_callback(f"📈 Optimized result: {optimized_tokens} tokens used, confidence: {optimized_confidence:.4f}")
        update_callback("🎉 Analysis complete - comparing baseline vs optimized approaches...")

        # --- Format Final Comparison ---
        result_string = "\n" + "="*80
        result_string += "\n                      J.A.R.V.I.S. NAPOLEON RIDDLE DEMO RESULTS"
        result_string += "\n" + "="*80
        result_string += f"\n\n--- PROMPT ---\n{DEMO_PROMPT}"
        
        # Determine if the answers are correct
        baseline_correct = "napoleon" in baseline_response.lower() if baseline_response else False
        optimized_correct = "napoleon" in optimized_response.lower() if optimized_response else False
        
        # Format baseline results with correctness indicator
        result_string += "\n\n--- BASELINE AGENT (Naive Mode) ---"
        result_string += f"\nToken Cost: {baseline_tokens}"
        result_string += f"\nConfidence: {baseline_confidence:.4f}"
        result_string += f"\nCorrect Answer: {'✅ YES' if baseline_correct else '❌ NO'}"
        result_string += f"\nResponse: {baseline_response}"
        
        # Format optimized results with correctness indicator
        result_string += "\n\n--- J.A.R.V.I.S. FRAMEWORK (Optimized) ---"
        result_string += f"\nToken Cost: {optimized_tokens}"
        result_string += f"\nConfidence: {optimized_confidence:.4f}"
        result_string += f"\nCorrect Answer: {'✅ YES' if optimized_correct else '❌ NO'}"
        result_string += f"\nResponse: {optimized_response}"
        
        # Add summary comparison
        result_string += "\n\n--- PERFORMANCE COMPARISON ---"
        result_string += f"\nToken Efficiency: {'✅ Better' if optimized_tokens < baseline_tokens else '❌ Worse'} ({baseline_tokens - optimized_tokens:+d} tokens)"
        result_string += f"\nConfidence: {'✅ Better' if optimized_confidence > baseline_confidence else '❌ Worse'} ({optimized_confidence - baseline_confidence:+.4f})"
        result_string += f"\nAnswer Correctness: {('Both correct' if baseline_correct and optimized_correct else 'Both incorrect' if not baseline_correct and not optimized_correct else 'Only optimized correct' if optimized_correct else 'Only baseline correct')}"
        
        result_string += "\n\n" + "="*80

        update_callback(result_string)

    except Exception as e:
        log.error("Demo runner failed with an exception.", exc_info=True)
        update_callback(f"Demo Runner ERROR: {e}")