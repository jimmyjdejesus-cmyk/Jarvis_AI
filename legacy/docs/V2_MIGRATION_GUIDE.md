# Jarvis AI V2 Migration Guide

## Overview

Jarvis AI V2 introduces a new LangGraph-based architecture that provides more sophisticated agent reasoning and better tool integration. This guide helps you migrate from V1 to V2.

## What's New in V2

### 🚀 Core Features

- **LangGraph Workflow**: Stateful, cyclical reasoning with Plan → Code → Test → Reflect loops
- **LangChain Tools**: Standardized tool system with `@tool` decorators
- **Conditional Edges**: Intelligent error handling and graceful degradation
- **Workflow Visualization**: LangGraphUI integration for visual debugging
- **Enhanced Backend**: FastAPI service for better scalability

### 🧠 Improved Agent Logic

- **Planner Node**: Sophisticated task analysis and planning
- **CodeWriter Node**: Enhanced code generation with context awareness
- **Debugger Node**: Automated testing and validation
- **Critic Node**: Self-reflection and quality assessment
- **ToolExecutor Node**: Robust tool execution with error handling

## Migration Strategy

### 1. Enabling V2 Architecture

**In the Streamlit UI:**
1. Open the sidebar
2. Look for "🚀 V2 Architecture" section
3. Check "Enable LangGraph V2"
4. The system will show status indicators

**Programmatically:**
```python
from agent.core.core import JarvisAgent

agent = JarvisAgent(
    # ... other parameters ...
    use_langgraph=True  # Enable V2
)
```

### 2. Installing Dependencies

V2 requires additional dependencies:

```bash
# Install enhanced requirements
pip install -r requirements_enhanced.txt

# Or install specific V2 dependencies
pip install langchain langchain-core langchain-community
pip install langgraph
pip install fastapi uvicorn
```

### 3. Configuration Updates

V2 introduces new configuration options in `config.yaml`:

```yaml
v2:
  enabled: true
  backend_url: "http://localhost:8001"
  langgraph_checkpoint_path: "./checkpoints/jarvis_agent.db"
  max_iterations: 15
  expert_model: "llama3.2"
  use_langchain_tools: true
  fallback_to_v1: true
  workflow_visualization: true
  langgraphui_enabled: false
```

### 4. Legacy Code Handling

#### Functional Code Reuse
- ✅ **Keep**: Working V1 tools and utilities
- ✅ **Import**: Existing agent logic into V2 nodes
- ✅ **Extend**: V1 functionality with V2 capabilities

#### Legacy Reference
- 📁 **Archive**: Only move to `old/` if completely replaced
- 🔄 **Gradual**: Incremental migration approach
- 📚 **Reference**: Use `read_legacy_file()` tool for historical access

#### Example Migration Pattern
```python
# Before (V1)
def old_tool_function(params):
    # Legacy implementation
    pass

# After (V2)
from langchain_core.tools import tool

@tool
def new_tool_function(params: str) -> str:
    """
    Enhanced tool with proper documentation for LangGraph agent.
    
    Args:
        params: Description of parameters
        
    Returns:
        Description of return value
    """
    # Reuse V1 logic where applicable
    # Add V2 enhancements
    pass
```

### 5. Running V2 Backend

#### Development Mode
```bash
# Start V2 backend with auto-reload
python scripts/start_v2_backend.py --reload

# Or directly with uvicorn
uvicorn agent.core.langgraph_backend:app --reload --port 8001
```

#### Production Mode
```bash
# Start V2 backend for production
python scripts/start_v2_backend.py --host 0.0.0.0 --port 8001
```

#### Docker Deployment
```dockerfile
# Add to your Dockerfile
COPY requirements_enhanced.txt .
RUN pip install -r requirements_enhanced.txt

# Expose V2 backend port
EXPOSE 8001

# Start both services
CMD ["python", "scripts/start_v2_backend.py"]
```

## Testing V2 Integration

### Automated Testing
```bash
# Run V2 integration tests
python scripts/test_v2_integration.py
```

### Manual Testing
1. **Enable V2** in the sidebar
2. **Ask questions** that involve multiple steps
3. **Check status** indicators for V2 availability
4. **Observe workflow** through enhanced reasoning display

### Example Test Queries
- "Help me review this Python code and generate tests"
- "Search for information about machine learning and create a summary"
- "List files in the current directory and analyze the project structure"

## Troubleshooting

### Common Issues

#### V2 Dependencies Missing
```
🟡 V2 LangGraph: Dependencies missing
```
**Solution**: Install missing packages
```bash
pip install langgraph langchain langchain-core
```

#### Backend Connection Failed
```
❌ Backend not available
```
**Solution**: Start the V2 backend service
```bash
python scripts/start_v2_backend.py
```

#### Fallback to V1 Mode
```
ℹ️ Using V1 compatibility mode
```
**Solution**: This is expected when V2 is disabled or unavailable

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### 1. Gradual Migration
- Start with V2 enabled but fallback enabled
- Test thoroughly before disabling V1 compatibility
- Monitor performance and adjust max_iterations

### 2. Tool Development
- Use `@tool` decorator for new tools
- Include comprehensive docstrings
- Handle errors gracefully with try/catch

### 3. Configuration Management
- Use environment variables for production settings
- Keep sensitive data (API keys) secure
- Version control your configuration files

### 4. Performance Optimization
- Adjust `max_iterations` based on your use case
- Monitor checkpoint database size
- Use appropriate models for your hardware

## Migration Checklist

- [ ] Install V2 dependencies (`pip install -r requirements_enhanced.txt`)
- [ ] Test V2 availability (`python scripts/test_v2_integration.py`)
- [ ] Enable V2 in Streamlit UI
- [ ] Configure V2 settings in config.yaml
- [ ] Start V2 backend service
- [ ] Test basic functionality with simple queries
- [ ] Test complex workflows
- [ ] Monitor performance and adjust settings
- [ ] Update deployment scripts for production
- [ ] Train team on new features and capabilities

## Getting Help

### Resources
- **Documentation**: Check `docs/` directory for detailed guides
- **Examples**: See `tools/` directory for tool implementations
- **Tests**: Review `scripts/test_v2_integration.py` for usage patterns

### Support Channels
- Open GitHub issues for bugs
- Check existing issues for known problems
- Contribute improvements via pull requests

## Rollback Plan

If you need to revert to V1:

1. **Disable V2** in the sidebar (uncheck "Enable LangGraph V2")
2. **Restart** the Streamlit application
3. **Verify** V1 functionality is working
4. **Remove V2 dependencies** if needed (optional)

The system is designed to gracefully fall back to V1 when V2 is unavailable.