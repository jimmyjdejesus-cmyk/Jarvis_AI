# Tuning Critic Behavior

Effective critic modules help the meta-intelligence core catch issues early and guide retries.

## Weighting Feedback
- Assign confidence scores to each critic.
- Increase weight for high or critical severity items.
- Prioritize critics with strong historical accuracy.

## Argument Synthesis
- Combine related critic messages into a single argument.
- Surface the highest severity so the system can decide on retries.
- Log synthesized arguments for later review.

## Adaptive Retries
- Retry failed tasks when critics report high or critical problems.
- Use exponential backoff to avoid rapid repeat failures.
- Track retry counts and success rates in analytics.

## Monitoring
- Continuously log success rates and iteration counts.
- Review analytics to tune critic thresholds and retry limits.

These practices keep critic feedback actionable while maintaining system reliability.
