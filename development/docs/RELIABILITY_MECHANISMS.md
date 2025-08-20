# Fallback & Reliability Mechanisms Documentation

This document describes the implementation of Issue #28: Fallback & Reliability Mechanisms for Jarvis AI.

## Overview

The reliability system provides graceful degradation and fallback mechanisms to ensure Jarvis AI continues operating even when services fail or resources are limited.

## Architecture

### Core Components

1. **ReliabilityManager** (`development/agent/core/reliability.py`)
   - Central manager for system reliability and fallback mechanisms
   - Monitors system health and switches operation modes
   - Implements recovery strategies for different failure scenarios

2. **EnhancedRAGCache** (`development/agent/core/rag_fallback.py`)
   - Enhanced caching system with persistent storage
   - Provides offline knowledge access when services are unavailable
   - Emergency response generation for critical situations

3. **ReliabilityWorkflow** (`development/agent/workflows/reliability_workflow.py`)
   - LangGraph workflow for managing degraded operations
   - State transitions for graceful degradation
   - Conditional workflows and error recovery paths

4. **ReliabilityMonitor** (`development/agent/ui/reliability_monitor.py`)
   - UI components for system health visualization
   - Real-time monitoring dashboard
   - Degraded mode interface for users

## Operation Modes

The system supports five operation modes with graceful degradation:

### 1. FULL Mode
- All features available
- Web RAG enabled
- Full processing capabilities
- Real-time external connections

### 2. LOCAL_ONLY Mode  
- No web RAG, local processing only
- Local knowledge base available
- File-based context processing
- Limited external connectivity

### 3. OFFLINE Mode
- Cached knowledge only
- No external connections
- Persistent cache access
- Emergency responses available

### 4. BASIC Mode
- Minimal functionality
- Basic completion only
- Limited processing capabilities
- Essential operations only

### 5. EMERGENCY Mode
- Critical systems only
- Most features disabled
- Emergency responses only
- System administrator notification

## Key Features

### Degraded Operation Modes

**Offline Mode with Cached Knowledge Only**
- Persistent cache storage with TTL management
- Local knowledge base for common queries
- File-based context extraction when available
- Emergency response generation

**Local-Only Mode without Web RAG**
- Disables external API calls
- Uses local processing only
- Maintains file analysis capabilities
- Fallback to cached results

**Basic Completion Mode for Low-Resource Environments**
- Minimal memory footprint
- Essential features only
- Reduced processing overhead
- Critical functionality preserved

### Error Recovery

**Automatic Ollama Service Monitoring**
- Real-time health checks
- Service restart attempts
- Model availability monitoring
- Connection retry with exponential backoff

**Model Reload on Corruption Detection**
- Model cache corruption detection
- Automatic cache clearing and reload
- Service recovery coordination
- Graceful fallback during reload

**Graceful Degradation Pathways**
- Automated mode switching based on health
- Recovery attempt coordination
- User notification of limitations
- Administrator escalation for critical issues

## Lang Ecosystem Integration

### LangChain Components
- Error handling chains for retry logic
- Fallback mechanisms for service failures
- Robust operation decorators
- Exception recovery strategies

### LangGraph Workflows
- State management for degraded modes
- Conditional workflows for error recovery
- Decision trees for mode switching
- Recovery attempt coordination

### LangSmith Monitoring (Future)
- Real-time system health tracking
- Error pattern analysis and alerting
- Performance tracking across modes
- Distributed reliability coordination

### LangGraphUI Components
- System health visualization
- Degraded mode status display
- Recovery progress tracking
- Administrator intervention interface

## Usage Examples

### Basic Usage

```python
from agent.core.reliability import get_reliability_manager
from agent.workflows.reliability_workflow import execute_reliability_check

# Get current system status
reliability_manager = get_reliability_manager()
status = reliability_manager.get_system_status()
print(f"Current mode: {status['mode']}")
print(f"System state: {status['state']}")

# Execute reliability check
result = execute_reliability_check("system health check")
print(f"Health check result: {result['response']}")
```

### Offline RAG Usage

```python
from agent.core.rag_fallback import offline_rag_answer

# Use offline RAG when services are unavailable
response = offline_rag_answer(
    prompt="What can you do in offline mode?",
    files=[],
    mode="offline"
)
print(response)
```

### UI Integration

```python
import streamlit as st
from agent.ui.reliability_monitor import render_reliability_dashboard

# Render reliability dashboard in Streamlit
render_reliability_dashboard()
```

## Testing

Comprehensive tests are provided in `development/tests/test_reliability.py`:

- **ReliabilityManager Tests**: Mode switching, configuration, service monitoring
- **EnhancedRAGCache Tests**: Caching, expiration, emergency responses
- **OfflineRAGHandler Tests**: Local knowledge, file context, fallback chains
- **ReliabilityWorkflow Tests**: Workflow execution, state transitions
- **Integration Tests**: Full degradation scenarios, end-to-end functionality
- **Error Scenario Tests**: Corruption handling, missing dependencies

Run tests with:
```bash
cd development
PYTHONPATH=/path/to/development python tests/test_reliability.py
```

## Configuration

The reliability system can be configured through the ReliabilityManager constructor:

```python
config = {
    "monitoring_enabled": True,  # Enable background monitoring
    "cache_size_mb": 100,        # Cache size limit
    "ttl_hours": 24,             # Cache entry TTL
    "max_retries": 3,            # Recovery attempt limit
    "escalation_threshold": 2    # Administrator escalation threshold
}

reliability_manager = ReliabilityManager(config)
```

## Integration with Existing Systems

The reliability system is designed to enhance existing Jarvis AI systems without replacement:

1. **Extends existing error handling** from `legacy/agent/core/error_handling.py`
2. **Enhances existing RAG cache** from `legacy/agent/features/rag_handler.py`  
3. **Improves Ollama monitoring** from `legacy/scripts/ollama_client.py`
4. **Maintains backward compatibility** with current interfaces

## Monitoring and Alerts

### Health Check Metrics
- Service availability (Ollama, RAG, Cache)
- Response times and performance
- Error rates and recovery success
- Cache hit rates and efficiency

### Alerting Conditions
- Critical service failures
- Repeated recovery attempts
- Cache corruption detection
- Emergency mode activation

### Dashboard Features
- Real-time system status
- Operation mode indicators
- Service health grid
- Recent events timeline
- Cache statistics

## Future Enhancements

1. **LangSmith Integration**: Real-time monitoring and alerting
2. **LangGraph Platform**: Distributed reliability coordination
3. **Predictive Health**: ML-based failure prediction
4. **Auto-scaling**: Dynamic resource adjustment
5. **Custom Recovery**: User-defined recovery strategies

## Support and Troubleshooting

### Common Issues

**System stuck in emergency mode**
- Check service logs for errors
- Verify Ollama service status
- Clear cache if corrupted
- Contact administrator if persistent

**Cache not persisting**
- Check directory permissions
- Verify disk space availability
- Review cache configuration
- Check for file system errors

**Degraded mode not recovering**
- Check network connectivity
- Verify service availability
- Review recovery attempt logs
- Force mode switch if needed

### Log Locations
- System logs: `logs/jarvis.log`
- Cache metadata: `cache/cache_metadata.json`
- Reliability events: In-memory fallback history

### Recovery Commands
```python
# Force full mode (admin only)
reliability_manager.force_mode_switch(OperationMode.FULL, "Admin override")

# Clear corrupted cache
reliability_manager._recover_cache_service()

# Check system health
health_report = reliability_manager._check_system_health()
```

This implementation provides robust fallback and reliability mechanisms that ensure Jarvis AI continues operating effectively even under adverse conditions.