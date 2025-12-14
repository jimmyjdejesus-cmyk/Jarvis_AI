"""OpenRouter API client for cloud model access"""
import os
import requests
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

        # Free models (try these first!)
        self.free_models = {
            "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct:free",
            "mistral-7b": "mistralai/mistral-7b-instruct:free",
            "gemma-7b": "google/gemma-7b-it:free",
        }

        # Paid models (for complex tasks)
        self.paid_models = {
            "claude-sonnet": "anthropic/claude-3-5-sonnet-20241022",
            "gpt-4o": "openai/gpt-4o",
            "claude-opus": "anthropic/claude-3-opus-20240229",
            "gpt-4-turbo": "openai/gpt-4-turbo-2024-04-09"
        }

        # Cost tracking
        self.cost_limit = float(os.getenv("MAX_CLOUD_COST_PER_DAY", "5.00"))
        self.current_cost = 0.0

    def _check_cost_limit(self) -> bool:
        """Check if we've exceeded the daily cost limit"""
        return self.current_cost >= self.cost_limit

    def _get_available_free_models(self) -> List[str]:
        """Get list of available free models"""
        return list(self.free_models.values())

    def _get_available_paid_models(self) -> List[str]:
        """Get list of available paid models"""
        return list(self.paid_models.values())

    def get_model_for_complexity(self, complexity: str) -> str:
        """Get best model for complexity level"""
        if complexity == "high":
            return self.paid_models["claude-sonnet"]
        elif complexity == "medium":
            return self.paid_models["gpt-4o"]
        else:  # low
            # Try free first, but have paid fallback
            return self.free_models["llama-3.1-8b"]

    async def generate(
        self,
        prompt: str,
        model: str = "meta-llama/llama-3.1-8b-instruct:free",
        max_tokens: int = 2048,
        complexity: str = "low"
    ) -> str:
        """Generate response with cloud-first strategy"""

        # Check cost limit
        if self._check_cost_limit():
            raise Exception(f"Daily cost limit of ${self.cost_limit} exceeded")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/jimmyjdejesus-cmyk/Jarvis_AI",
            "X-Title": "Jarvis AI Assistant",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]

                # Estimate cost (rough approximation)
                cost_estimate = self._estimate_cost(model, len(prompt), len(result))
                self.current_cost += cost_estimate

                logger.info(f"OpenRouter success: {model} (complexity: {complexity}, cost: ${cost_estimate:.4f})")
                return result
            else:
                logger.error(f"OpenRouter error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter error: {response.status_code}")

        except Exception as e:
            logger.error(f"OpenRouter request failed: {e}")
            raise

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Rough cost estimation per request"""
        # Simplified cost calculation - in production you'd use actual pricing
        cost_per_1k_input = 0.001  # $0.001 per 1K input tokens for paid models
        cost_per_1k_output = 0.004  # $0.004 per 1K output tokens for paid models

        # Free models cost $0
        if ":free" in model:
            return 0.0

        input_cost = (input_tokens / 1000) * cost_per_1k_input
        output_cost = (output_tokens / 1000) * cost_per_1k_output
        return input_cost + output_cost

    def reset_daily_cost(self):
        """Reset daily cost counter (call this daily)"""
        self.current_cost = 0.0

    def get_cost_status(self) -> Dict[str, Any]:
        """Get current cost status"""
        return {
            "current_cost": self.current_cost,
            "cost_limit": self.cost_limit,
            "remaining_budget": max(0, self.cost_limit - self.current_cost),
            "is_over_limit": self._check_cost_limit()
        }
