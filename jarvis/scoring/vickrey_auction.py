"""Vickrey auction based scoring for agent outputs.

This module implements a simple second-price sealed-bid auction used to
select the most valuable agent output while encouraging truthful bidding.
It also returns basic diversity and utility metrics that callers can use to
track exploration quality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Candidate:
    """Represents an agent's bid in the auction."""

    agent: str
    bid: float
    content: str


@dataclass
class AuctionResult:
    """Outcome of a Vickrey auction."""

    winner: Candidate
    price: float
    rankings: List[Candidate]
    metrics: Dict[str, float]


def run_vickrey_auction(candidates: List[Candidate]) -> AuctionResult:
    """Run a Vickrey auction over provided candidates.

    Parameters
    ----------
    candidates:
        List of :class:`Candidate` objects participating in the auction.

    Returns
    -------
    AuctionResult
        The auction outcome containing the winner, clearing price, ranking of
        bids, and simple exploration metrics.
    """

    if not candidates:
        raise ValueError("No candidates supplied")

    ordered = sorted(candidates, key=lambda c: c.bid, reverse=True)
    winner = ordered[0]
    price = ordered[1].bid if len(ordered) > 1 else winner.bid

    diversity = float(len({c.content for c in ordered}))
    avg_bid = sum(c.bid for c in ordered) / len(ordered)

    metrics = {"diversity": diversity, "avg_bid": avg_bid}

    return AuctionResult(winner=winner, price=price, rankings=ordered, metrics=metrics)


__all__ = ["Candidate", "AuctionResult", "run_vickrey_auction"]
