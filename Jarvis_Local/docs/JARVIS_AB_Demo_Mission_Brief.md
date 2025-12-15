# J.A.R.V.I.S. A/B Demo Mission Brief

## Purpose
This demo showcases a direct comparison between a **Baseline Agent**
(minimal prompting, no reasoning) and the **J.A.R.V.I.S. Framework**
(multi-agent, advanced reasoning, remediation).

The goal is to highlight the impact of agent architecture and prompting
strategies on answer quality, reasoning, and efficiency.

## Scenario
**Prompt:**
> If Napoleon had won the Battle of Waterloo, what would the 16th President's grandfather's name have been?

This riddle requires historical knowledge, logical reasoning, and the ability to handle hypothetical scenarios.

## Demo Structure
1. **Run 1: Baseline Agent**
   - Uses a minimal system prompt: "Answer questions directly and concisely."
   - No chain-of-thought, no specialist routing, no remediation.
   - Provides a direct answer with minimal explanation.

2. **Run 2: J.A.R.V.I.S. Framework**
   - Uses advanced multi-agent architecture:
     - MetaAgent: Analyzes and routes the request
     - ResearchAgent: Gathers historical context and reasoning
     - Remediation: If confidence is low, escalates to another specialist
   - Provides detailed reasoning, step-by-step analysis, and improved accuracy.

## What to Look For
- **Answer Quality:** Is the answer correct and well-reasoned?
- **Reasoning:** Does the agent explain its thought process?
- **Token Efficiency:** How many tokens are used for each approach?
- **Confidence:** How confident is the agent in its answer?

## Results (Example)
| Approach         | Token Cost | Confidence | Correct | Reasoning |
|------------------|------------|------------|---------|-----------|
| Baseline Agent   | 750        | 0.43       | Yes     | Minimal   |
| J.A.R.V.I.S.     | 100        | 0.09       | Yes     | Detailed  |

## Takeaway
This demo illustrates the difference between naive direct answering and advanced agent-based reasoning. The J.A.R.V.I.S. framework is designed to deliver:
- More accurate answers
- Better reasoning and explanations
- Efficient use of resources

**Handout prepared: September 3, 2025**
