# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# evaluation.py
from orchestrator import Orchestrator
from logger_config import log

# --- Test Suite Definition ---
# Each test is a dictionary with a name, a prompt, and a validator function.
# The validator function takes the model's response and returns True (pass) or False (fail).
TEST_SUITE = [
    {
        "name": "Forceful Chain of Though (CoT)",
        "prompt": 
        """
        You are a meticulous logic and math expert. Your task is to solve the following problem by thinking step-by-step.
        1.  First, identify the known variables.
        2.  Second, calculate the head start of the first vehicle.
        3.  Third, calculate the difference in speed (relative speed).
        4.  Fourth, use the head start and relative speed to determine the time to catch up.
        5.  Finally, add that time to the second vehicle's departure time to find the final answer.

        Problem: A train leaves City A at 8 AM traveling at 60 mph, and a car leaves City A at 9 AM traveling at 70 mph in the same direction. At what time will the car catch up to the train?

        Begin your step-by-step thinking now.
        """,
        "validator": lambda response: "3 pm" in response.lower() or "3:00" in response
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
    {
        "name": "Specialist Code Test",
        "prompt": "Please write a python script that prints the numbers from 1 to 10.",
        "validator": lambda response: "for i in range" in response and "print(i)" in response
    },
    # ... Add more tests as you think of them ...
]

def run_evaluation():
    log.info("--- STARTING EVALUATION HARNESS ---")
    orchestrator = Orchestrator()
    
    total_token_cost = 0
    passed_count = 0
    failed_tests = []
    total_count = len(TEST_SUITE)

    for i, test in enumerate(TEST_SUITE):
        test_name = test["name"]
        prompt = test["prompt"]
        validator = test["validator"]

        log.info(f"--- Running Test {i+1}/{total_count}: {test_name} ---")

        # Get the response and token cost from orchestrator
        response, tokens_used, confidence = orchestrator.handle_request(prompt)
        total_token_cost += tokens_used

        # Validate the response
        try:
            is_pass = validator(response)
            if is_pass:
                log.info(f"--- RESULT: PASSED ---")
                passed_count += 1
            else:
                log.warning(f"--- RESULT: FAILED ---")
                log.warning(f"   - Response was: {response}")
                failed_tests.append(test_name) 
        except Exception as e:
            log.error(f"--- RESULT: ERROR ---")
            log.error(f"   - Validator function failed with error: {e}")
            log.error(f"   - Response was: {response}")
            failed_tests.append(test_name)

    log.info("--- EVALUATION HARNESS COMPLETE ---")
    log.info(f"--- FINAL SCORE: {passed_count} / {total_count} | Total Token Cost: {total_token_cost} ---")

    # --- Returning a dictionary with results ---
    return {
        "passed": passed_count,
        "total" : total_count,
        "failed": failed_tests,
        "total_tokens": total_token_cost
    }

if __name__ == "__main__":
    run_evaluation()