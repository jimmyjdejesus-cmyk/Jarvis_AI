"""Galaxy Model analysis API.

This module exposes a FastAPI app with an ``/analyze`` endpoint implementing
an approximation of the DeepConf "Galaxy Model" pipeline.  It generates
multiple reasoning traces, scores confidence, and clusters semantically
similar traces for visualization on the frontend.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import List, Dict, Any
import numpy as np

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util

from . import llm_generator

K = 64
GROUP_SIZE = 2048
SIMILARITY_THRESHOLD = 0.7


class PromptRequest(BaseModel):
    """Request model containing the prompt to analyze."""

    prompt: str


router = APIRouter()


@lru_cache(maxsize=1)
def get_similarity_model() -> SentenceTransformer:
    """Lazily load and cache the sentence transformer model."""

    return SentenceTransformer("all-MiniLM-L6-v2")


def calculate_lowest_group_confidence(trace: str, group_size: int) -> float:
    """Approximate confidence by the lowest unique-token ratio in groups.

    Splits the trace into token groups of ``group_size`` and computes the ratio
    of unique tokens to total tokens for each group.  The minimum ratio across
    all groups acts as a lightweight confidence heuristic.
    """

    tokens = trace.split()
    if not tokens:
        return 0.0

    min_conf = float("inf")
    for i in range(0, len(tokens), group_size):
        group = tokens[i:i + group_size]
        if not group:
            continue
        unique_ratio = len(set(group)) / len(group)
        min_conf = min(min_conf, unique_ratio)
    return min_conf if min_conf != float("inf") else 0.0


def extract_answer(trace: str) -> str:
    """Extract the final answer from a ``\boxed{}`` tag if present."""

    match = re.search(r"\\boxed{([^}]+)}", trace)
    return match.group(1) if match else ""


@router.post("/analyze")
async def run_galaxy_analysis(request: PromptRequest) -> Dict[str, Any]:
    """Generate graph data for the Galaxy visualization."""

    raw_traces = llm_generator.generate_k_traces(request.prompt, K)

    trace_details = []
    for trace in raw_traces:
        confidence_score = calculate_lowest_group_confidence(trace, GROUP_SIZE)
        final_answer = extract_answer(trace)
        trace_details.append(
            {
                "full_text": trace,
                "confidence": confidence_score,
                "answer": final_answer,
            }
        )

    all_trace_texts = [t["full_text"] for t in trace_details]
    model = get_similarity_model()
    embeddings = model.encode(all_trace_texts, convert_to_tensor=True)
    cosine_scores = util.cos_sim(embeddings, embeddings)
    if hasattr(cosine_scores, "cpu"):
        cosine_scores = cosine_scores.cpu().numpy()
    else:
        cosine_scores = np.array(cosine_scores)

    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []
    for i, detail in enumerate(trace_details):
        nodes.append(
            {
                "id": f"trace_{i}",
                "confidence": detail["confidence"],
                "answer": detail["answer"],
                "full_text": detail["full_text"],
            }
        )
        for j in range(i + 1, len(trace_details)):
            similarity = float(cosine_scores[i, j])
            if similarity > SIMILARITY_THRESHOLD:
                links.append(
                    {
                        "source": f"trace_{i}",
                        "target": f"trace_{j}",
                        "strength": similarity,
                    }
                )

    return {"graph_data": {"nodes": nodes, "links": links}}


app = FastAPI()
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
