# tools/autotune.py
import config
from evaluation import run_evaluation
from logger_config import log

def find_optimal_threshold():
    threshold_range = [i * 0.5 for i in range(2, 31)] 

    best_result = {
        "threshold": None,
        "tokens": float('inf'),
        "score": -1
    }

    log.info("--- STARTING COST-AWARE AUTO-TUNER ---")
    log.info(f"Testing {len(threshold_range)} thresholds from {threshold_range[0]} to {threshold_range[-1]}...")

    for threshold in threshold_range:
        config.CONFIDENCE_THRESHOLD = threshold
        log.info(f"--- Testing threshold: {threshold:.2f} ---")

        results = run_evaluation()

        # We are looking for the CHEAPEST way to get the HIGHEST score.
        is_better_score = results["passed"] > best_result["score"]
        is_same_score_but_cheaper = (results["passed"] == best_result["score"]) and (results["total_tokens"] < best_result["tokens"])

        if is_better_score or is_same_score_but_cheaper:
            best_result["threshold"] = threshold
            best_result["tokens"] = results["total_tokens"]
            best_result["score"] = results["passed"]
            log.info(f"New best result! Threshold: {threshold}, Score: {results['passed']}/{results['total']}, Tokens: {results['total_tokens']}")

    log.info("--- AUTO-TUNER COMPLETE ---")

    if best_result["threshold"] is not None:
        log.info(f"Optimal threshold is {best_result['threshold']:.2f}, achieving a score of {best_result['score']} with a cost of {best_result['tokens']} tokens.")
        log.info("Update your config.py with this value.")
    else:
        log.warning("Auto-tuner could not find a successful configuration.")

if __name__ == "__main__":
    find_optimal_threshold()