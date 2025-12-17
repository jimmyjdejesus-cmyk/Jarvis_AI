# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



# utils/confidence.py
"""
Helper functions to optimize confidence calculations.
"""
import numpy as np
from collections import deque
from logger_config import log

def calculate_average_confidence(output):
    """Calculates the average token confidence from the model's output."""
    try:
        token_logprobs = output['choices'][0]['logprobs']['token_logprobs']
        if len(token_logprobs) > 1:
            avg_confidence = -np.mean(token_logprobs[1:])
            return avg_confidence
        return 0.0
    except (KeyError, IndexError, TypeError):
        return 0.0

def calculate_lowest_group_confidence(output, window_size=32):
    """Calculates the lowest average confidence over a sliding window of tokens."""
    try:
        token_logprobs = output['choices'][0]['logprobs']['token_logprobs']
        if len(token_logprobs) <= 1: return 0.0

        confidences = [-lp for lp in token_logprobs[1:]]

        if len(confidences) < window_size:
            return np.mean(confidences) if confidences else 0.0

        min_avg_confidence = float('inf')
        current_sum = sum(confidences[:window_size])
        min_avg_confidence = current_sum / window_size

        for i in range(window_size, len(confidences)):
            current_sum += confidences[i] - confidences[i - window_size]
            current_avg = current_sum / window_size
            if current_avg < min_avg_confidence:
                min_avg_confidence = current_avg

        return min_avg_confidence
    except (KeyError, IndexError, TypeError):
        log.warning("Could not calculate group confidence due to missing logprobs.")
        return 0.0
    
def calculate_lowest_single_token_confidence(output, window_size=32):
    """Calculates the lowest confidence of any single token in a sliding window."""
    try:
        token_logprobs = output['choices'][0]['logprobs']['token_logprobs']
        window = deque(maxlen=window_size)
        for logprob in token_logprobs[1:]:
            window.append(-logprob)

        if window:
            return min(window)
        return 0.0
    except (KeyError, IndexError, TypeError):
        log.warning("Could not calculate single-token confidence due to missing logprobs.")
        return 0.0