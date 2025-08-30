# evaluation.py
from orchestrator import Orchestrator
from logger_config import log

# --- Test Suite Definition ---
# Each test is a dictionary with a name, a prompt, and a validator function.
# The validator function takes the model's response and returns True (pass) or False (fail).
TEST_SUITE = [
    {
        "name": "Simple Reasoning",
        "prompt": "If a train leaves City A at 8 AM traveling at 60 mph, and a car leaves City A at 9 AM traveling at 70 mph in the same direction, at what time will the car catch up to the train?",
        "validator": lambda response: "12 PM" in response or "noon" in response.lower()
    },
    {
        "name": "Basic Code Generation",
        "prompt": "Write a simple python function that takes two numbers and returns their sum.",
        "validator": lambda response: "def" in response and "return" in response and "+" in response
    },
    {
        "name": "Instruction Following",
        "prompt": "Respond to this question with a single word: What is the capital of France?",
        "validator": lambda response: len(response.split()) <= 2 and "paris" in response.lower()
    },
    # ... Add more tests as you think of them ...
]

def run_evaluation():
    log.info("--- STARTING EVALUATION HARNESS ---")
    orchestrator = Orchestrator()

    passed_count = 0
    total_count = len(TEST_SUITE)

    for i, test in enumerate(TEST_SUITE):
        test_name = test["name"]
        prompt = test["prompt"]
        validator = test["validator"]

        log.info(f"--- Running Test {i+1}/{total_count}: {test_name} ---")

        # Get the response from your agent
        response = orchestrator.handle_request(prompt)

        # Validate the response
        try:
            is_pass = validator(response)
            if is_pass:
                log.info(f"--- RESULT: PASSED ---")
                passed_count += 1
            else:
                log.warning(f"--- RESULT: FAILED ---")
                log.warning(f"   - Response was: {response}")

        except Exception as e:
            log.error(f"--- RESULT: ERROR ---")
            log.error(f"   - Validator function failed with error: {e}")
            log.error(f"   - Response was: {response}")

    log.info("--- EVALUATION HARNESS COMPLETE ---")
    log.info(f"--- FINAL SCORE: {passed_count} / {total_count} PASSED ---")
    return passed_count, total_count

if __name__ == "__main__":
    run_evaluation()