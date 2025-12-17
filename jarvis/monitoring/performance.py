# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""Performance tracking and monitoring utilities for Jarvis.

This module provides lightweight performance tracking functionality for
monitoring system operations, failed steps, and retry behavior. It's designed
as a simplified implementation for testing and development scenarios.

The real performance tracking implementation would be more sophisticated with
external monitoring integration, but this shim provides enough functionality
to satisfy unit tests and basic monitoring needs.

Key Features:
- Simple event-based performance tracking
- Failed step counting
- Retry attempt monitoring
- Reset capability for clean state
- Minimal dependencies

Note:
This is a simplified implementation intended for testing and development.
Production use should implement proper metrics collection, persistence,
and integration with external monitoring systems.
"""

from __future__ import annotations

from typing import Dict


class PerformanceTracker:
    """Simple performance tracker for monitoring system operations.
    
    Provides basic performance monitoring capabilities by tracking failed
    steps and retry attempts. This is a lightweight implementation designed
    for testing and development scenarios.
    
    The tracker maintains simple metrics counters that can be used to:
    - Monitor system reliability through failed step counts
    - Track retry behavior and efficiency
    - Identify performance bottlenecks
    
    Example:
        >>> tracker = PerformanceTracker()
        >>> tracker.record_event("step_1", success=True)
        >>> tracker.record_event("step_2", success=False, attempt=1)
        >>> tracker.record_event("step_2", success=True, attempt=2)
        >>> tracker.metrics
        {"failed_steps": 1, "retry_attempts": 1}
        
    Attributes:
        metrics: Dictionary containing performance metrics counters
    """

    def __init__(self) -> None:
        """Initialize the PerformanceTracker with zeroed metrics.
        
        Sets up internal metrics dictionary for tracking failed steps
        and retry attempts. All counters start at zero.
        """
        self.metrics: Dict[str, int] = {
            "failed_steps": 0,     # Count of failed execution steps
            "retry_attempts": 0,   # Count of retry attempts (attempt > 1)
        }

    def record_event(self, name: str, success: bool, attempt: int = 1) -> None:
        """Record a performance event for tracking.
        
        Updates performance metrics based on the event outcome and attempt count.
        Failed events increment the failed_steps counter, and any event with
        attempt > 1 increments the retry_attempts counter.
        
        Args:
            name: Identifier for the event being recorded
            success: Boolean indicating if the event was successful
            attempt: Attempt number (1 for first attempt, >1 for retries)
        """
        # Track failed steps
        if not success:
            self.metrics["failed_steps"] += 1
            
        # Track retry attempts (any attempt beyond the first)
        if attempt > 1:
            self.metrics["retry_attempts"] += 1

    def reset(self) -> None:
        """Reset all performance metrics to zero.
        
        Clears all tracked metrics and returns the tracker to its initial
        state. Useful for starting fresh monitoring sessions or cleaning
        up after testing scenarios.
        """
        self.metrics = {k: 0 for k in self.metrics}
