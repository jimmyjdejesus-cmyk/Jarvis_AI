# Jarvis AI Cloud-First Setup Guide

## 🚀 Quick Start (3 Steps)

### 1. Get OpenRouter API Key
1. Visit https://openrouter.ai/keys
2. Create a free account
3. Generate an API key
4. Copy the key (starts with `sk-or-v1-`)

### 2. Configure Environment
Create a `.env` file in the Jarvis_AI root directory:

```bash
# ========================================
# CLOUD-FIRST CONFIGURATION
# ========================================

# OpenRouter API key (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Routing Strategy (recommended: cloud_first)
ROUTE_STRATEGY=cloud_first          # Options: cloud_first, local_first, balanced
PREFER_FREE_CLOUD=true              # Try free OpenRouter models first
ALLOW_LOCAL_FALLBACK=true           # Use Ollama if cloud fails

# Cost Management (recommended settings)
MAX_CLOUD_COST_PER_DAY=5.00        # Stop using paid cloud at $5/day
SWITCH_TO_LOCAL_AFTER_LIMIT=true   # Use Ollama after hitting limit

# Ollama (Fallback only - cloud is primary)
OLLAMA_HOST=http://localhost:11434
OLLAMA_SMALL_MODEL=llama3.2:3b
OLLAMA_MEDIUM_MODEL=llama3:8b

# Logging (recommended for debugging)
LOG_LEVEL=INFO                      # Set to DEBUG to see routing decisions
LOG_ROUTING_DECISIONS=true          # Log why each model was selected
```

### 3. Install Ollama Models (Fallback)
```bash
# Install Ollama if not already installed
brew install ollama  # macOS
# OR visit https://ollama.ai/download for other platforms

# Pull models (these are used only as fallback when cloud fails)
ollama pull llama3.2:3b      # Fast, small (2GB) - for simple tasks
ollama pull llama3:8b         # Medium (5GB) - primary fallback model

# Test Ollama
ollama run llama3:8b "Hello world"
```

## 🎯 How Cloud-First Routing Works

### **Routing Logic:**

1. **Classify Task Complexity:**
   - **Low:** Simple Q&A, short responses (< 500 chars, basic queries)
   - **Medium:** Code generation, analysis, explanations (500-2000 chars, creative tasks)
   - **High:** Architecture, security audits, complex reasoning (> 2000 chars, expert tasks)

2. **Route Based on Complexity:**

   **LOW complexity:**
   - Try: OpenRouter free models (llama-3.1-8b-instruct:free)
   - If fails: Ollama local small (llama3.2:3b)
   - Cost: $0 (free tier)

   **MEDIUM complexity:**
   - Try: OpenRouter paid (GPT-4o, Claude Sonnet)
   - If fails: Ollama local medium (llama3:8b)
   - Cost: $0.002-0.01 per request

   **HIGH complexity:**
   - Try: OpenRouter premium (Claude Opus, GPT-4 Turbo)
   - If fails: OpenRouter paid (Claude Sonnet)
   - **NO LOCAL FALLBACK** (not good enough for complex tasks)
   - Cost: $0.01-0.05 per request

3. **Cost Controls:**
   - Daily limit: $5.00 (configurable)
   - Automatic fallback to local when limit reached
   - Free tier prioritization

## 🧪 Testing Your Setup

### Test Cloud Connection:
```bash
cd Jarvis_AI/legacy
python -c "
from jarvis.mcp.providers.openrouter import OpenRouterClient
client = OpenRouterClient()
result = client.generate('Write hello world in Python')
print('Cloud test result:', result[:100])
"
```

### Test Full Routing:
```bash
# Start the Jarvis server
python app/main.py

# In another terminal, test routing
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Write a Python function to calculate fibonacci"}],
    "prefer_free": true
  }'
```

### Test Cost Tracking:
```python
from jarvis.mcp.providers.openrouter import OpenRouterClient
client = OpenRouterClient()
status = client.get_cost_status()
print(f"Current cost: ${status['current_cost']:.2f}")
print(f"Remaining budget: ${status['remaining_budget']:.2f}")
```

## 📊 Model Performance

| Model | Context | Cost | Best For | Speed |
|-------|---------|------|----------|-------|
| llama-3.1-8b-instruct:free | 8K | $0 | Simple tasks | Fast |
| GPT-4o | 128K | $0.002/1K | Code, analysis | Medium |
| Claude Sonnet | 200K | $0.008/1K | Complex reasoning | Medium |
| Claude Opus | 200K | $0.015/1K | Maximum quality | Slow |
| llama3.2:3b (local) | 8K | $0 | Fallback | Fast |
| llama3:8b (local) | 8K | $0 | Fallback | Medium |

## 🔧 Troubleshooting

### "OpenRouter API key is required"
- Check that `OPENROUTER_API_KEY` is set in your `.env` file
- Verify the key starts with `sk-or-v1-`
- Make sure the `.env` file is in the Jarvis_AI root directory

### "Daily cost limit exceeded"
- Check `client.get_cost_status()` to see current usage
- Increase `MAX_CLOUD_COST_PER_DAY` in `.env`
- Call `client.reset_daily_cost()` to reset (do this daily)

### Cloud requests failing
- Check your internet connection
- Verify OpenRouter service status: https://status.openrouter.ai
- Try a different model in the complexity mapping

### Local fallback not working
- Ensure Ollama is running: `ollama serve`
- Check model is pulled: `ollama list`
- Verify `OLLAMA_HOST` is correct in `.env`

## 🎯 Pro Tips

1. **Start Conservative:** Begin with $1-2 daily limit until you understand usage
2. **Monitor Costs:** Check `LOG_ROUTING_DECISIONS=true` to see model selection logic
3. **Free Tier First:** Keep `PREFER_FREE_CLOUD=true` for cost control
4. **Local Fallback:** Always keep `ALLOW_LOCAL_FALLBACK=true` for reliability
5. **Complexity Hints:** Add keywords like "architecture", "security", "audit" to force high-complexity routing

## 🚀 Advanced Configuration

### Custom Complexity Classification:
```python
# In model_router.py, modify _classify_complexity()
custom_high_keywords = ["architecture", "security", "audit", "design", "system"]
custom_medium_keywords = ["write", "create", "debug", "review", "implement"]
```

### Custom Cost Limits:
```python
# Different limits for different task types
COST_LIMITS = {
    "coding": 10.00,      # More budget for coding tasks
    "research": 5.00,     # Standard for research
    "creative": 2.00      # Less for creative tasks
}
```

### Model Preferences:
```python
# Override default model selection
COMPLEXITY_MODELS = {
    "high": "anthropic/claude-3-opus-20240229",  # Always use best for high complexity
    "medium": "openai/gpt-4o",                   # GPT-4o for medium tasks
    "low": "meta-llama/llama-3.1-8b-instruct:free"  # Free for simple tasks
}
```

---

**🎉 You're now running Jarvis AI with cloud-first intelligence!**

The system will automatically choose the best model for each task while keeping costs under control and maintaining reliability through local fallbacks.
