# Benchmark Results

The table below compares the **balanced** pruning policy against a
**no-prune** baseline. Numbers are averaged over the four benchmark
scenarios (Q&A, code review, deep research and adversarial).

| Policy      | Tokens | Latency (s) | BQ Score | Novelty |
|-------------|-------:|------------:|---------:|--------:|
| Balanced    | 700    | 1.10        | 0.92     | 0.95    |
| No-prune    | 1000   | 1.00        | 0.90     | 0.90    |

Token savings: **30%**
Latency increase: **10%**
Quality: **+0.02 BQ**

Novelty values reflect the proportion of unique tokens per scenario.
