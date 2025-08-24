"""Discrete communication channel with bandwidth penalties.

This module provides :class:`BandwidthLimitedChannel`, a simple abstraction
that imposes latency based on message size and available bandwidth.  The
channel can be used to simulate constrained communication where larger
messages incur a delay proportional to their size.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any


class BandwidthLimitedChannel:
    """Communication channel that penalises large messages.

    Parameters
    ----------
    bandwidth:
        Maximum number of bytes that can be transmitted per second.  A message
        exceeding this limit induces a proportional delay before it becomes
        available to receivers.
    """

    def __init__(self, bandwidth: int) -> None:
        if bandwidth <= 0:
            raise ValueError("bandwidth must be positive")
        self.bandwidth = bandwidth
        self.total_penalty: float = 0.0

    async def transmit(self, message: Any) -> None:
        """Transmit a message applying a bandwidth penalty.

        The message is JSON serialised to estimate its size.  A delay equal to
        ``size / bandwidth`` seconds is introduced to model transmission time.

        Parameters
        ----------
        message:
            Arbitrary JSON‑serialisable payload to be sent through the channel.
        """
        payload = json.dumps(message)
        delay = len(payload) / self.bandwidth
        self.total_penalty += delay
        if delay > 0:
            await asyncio.sleep(delay)
