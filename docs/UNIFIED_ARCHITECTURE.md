# Jarvis AI - Unified Architecture

## Overview

Jarvis AI is now a unified multi-agent intelligence system that combines the advanced capabilities of the new agent framework with the robust legacy orchestration system. This document describes the unified architecture and how all components work together.

## Architecture Components

### 1. Configuration System
- **Unified Config**: Both GUI and backend use `~/.jarvis/config.json`
- **Environment Variables**: `.env` file support with automatic loading
- **Migration Tool**: `legacy/scripts/migrate_config.py` for seamless migration

### 2. Core Runtime
- **New Agent Manager**: Multi-agent coordination and task management
- **Ollama Client**: Local LLM integration with streaming support
- **Memory Systems**: Conversation memory and knowledge graph
- **Legacy Orchestration**: Mission planning and workflow execution

### 3. Bridge System
The bridge system connects new and legacy components:

#### Agent Bridge (`jarvis/agent_bridge.py`)
- Maps legacy agent types to new agent implementations
- Executes tasks using the new AgentManager
- Supports agent collaboration and coordination

#### Memory Bridge (`jarvis/memory_bridge.py`)
- Syncs conversation data between systems
- Migrates knowledge graph data
- Provides unified memory access

#### Workflow Bridge (`jarvis/workflow_bridge.py`)
- Connects research pipeline with legacy workflows
- Supports multi-agent collaboration workflows
- Handles benchmark and analysis workflows

#### Security Bridge (`jarvis/security_bridge.py`)
- Validates agent actions using new security systems
- Provides security auditing and monitoring
- Integrates with legacy security policies

#### Monitoring Bridge (`jarvis/monitoring_bridge.py`)
- Collects metrics from all system components
- Provides health monitoring and performance tracking
- Exports metrics for external monitoring tools

### 4. API Endpoints

#### Core Endpoints
- `GET /health` - System health check
- `GET /api/models` - Available LLM models
- `POST /api/chat` - Chat with the system
- `POST /api/chat/stream` - Streaming chat

#### Agent Endpoints
- `GET /api/agents` - List available agents
- `POST /api/agents/execute` - Execute agent task
- `POST /api/agents/collaborate` - Multi-agent collaboration
- `GET /api/agents/capabilities/{type}` - Agent capabilities

#### Memory Endpoints
- `GET /api/memory/conversations` - Recent conversations
- `GET /api/knowledge/search` - Knowledge graph search
- `POST /api/memory/sync/to-legacy` - Sync to legacy format
- `POST /api/memory/migrate` - Migrate all memory data

#### Workflow Endpoints
- `POST /api/workflows/execute` - Execute workflow
- `GET /api/workflows/capabilities` - Available workflows
- `GET /api/workflows/active` - Active workflows

#### Security Endpoints
- `POST /api/security/validate` - Validate agent action
- `GET /api/security/events` - Security events
- `POST /api/security/audit` - Security audit

#### Monitoring Endpoints
- `GET /api/monitoring/metrics` - System metrics
- `GET /api/monitoring/health` - Health status
- `GET /api/monitoring/performance` - Performance metrics

### 5. GUI Components

#### Main Window (`jarvis/gui/main_window.py`)
- Unified desktop interface
- Navigation between all system components
- Real-time status monitoring

#### Specialized Widgets
- **Chat Interface**: Direct interaction with agents
- **Agent Manager**: Create and manage agents
- **Research Pipeline**: Advanced research tools
- **Benchmark Widget**: Testing and evaluation
- **Diagnostics**: API endpoint testing
- **Settings**: Configuration management

## Getting Started

### 1. Installation
```bash
# Install the new repo
pip install -e "C:\Users\Student\Downloads\github_repos\jarvis-ai"

# Run config migration
python C:\Users\Student\.cursor\Jarvis_AI\legacy\scripts\migrate_config.py
```

### 2. Configuration
Create a `.env` file with your settings:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
API_HOST=127.0.0.1
API_PORT=8000
```

### 3. Running the System

#### Backend API
```bash
python -m uvicorn legacy.app.main:app --host 127.0.0.1 --port 8000
```

#### GUI Application
```bash
python C:\Users\Student\.cursor\Jarvis_AI\legacy\scripts\run_new_gui.py
```

#### CLI Interface
```bash
python -m jarvis "Your objective here"
```

### 4. Testing
```bash
# Run integration tests
python C:\Users\Student\.cursor\Jarvis_AI\legacy\scripts\test_integration.py

# Test specific components
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/models
```

## Key Features

### Multi-Agent System
- **Research Agent**: Literature search and analysis
- **Coding Agent**: Code generation and analysis
- **Curiosity Agent**: Creative exploration and hypothesis generation
- **Benchmark Agent**: Testing and evaluation
- **Critics**: Blue Team, Red Team, and Constitutional critics

### Advanced Capabilities
- **Streaming Chat**: Real-time conversation with streaming responses
- **Agent Collaboration**: Multiple agents working together on complex tasks
- **Research Pipeline**: Automated literature search and analysis
- **Knowledge Graph**: Persistent knowledge storage and retrieval
- **Security Monitoring**: Real-time security validation and auditing
- **Performance Monitoring**: System metrics and health monitoring

### Legacy Integration
- **Mission Planning**: Existing mission planning system
- **Workflow Engine**: Legacy workflow execution
- **Database Integration**: Neo4j and SQLite support
- **API Compatibility**: Maintains existing API endpoints

## Configuration Reference

### Environment Variables
- `OLLAMA_HOST`: Ollama server host (default: http://localhost:11434)
- `OLLAMA_MODEL`: Default model to use
- `API_HOST`: API server host (default: 127.0.0.1)
- `API_PORT`: API server port (default: 8000)
- `MAX_CONCURRENT_AGENTS`: Maximum concurrent agents (default: 5)
- `AGENT_TIMEOUT`: Agent task timeout in seconds (default: 300)

### Config File Structure
```json
{
  "ollama": {
    "host": "http://localhost:11434",
    "model": "llama3.1:8b-instruct-q4_K_M",
    "timeout": 120,
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "agents": {
    "max_concurrent": 5,
    "timeout": 300,
    "memory_limit_mb": 8192,
    "enable_logging": true,
    "collaboration_enabled": true
  },
  "research": {
    "arxiv_max_results": 50,
    "enable_web_search": true,
    "knowledge_graph_enabled": true
  },
  "gui": {
    "theme": "dark",
    "window_width": 1400,
    "window_height": 900
  }
}
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is running: `ollama serve`
   - Check OLLAMA_HOST environment variable
   - Verify model is available: `ollama list`

2. **Agent Manager Not Available**
   - Check if new repo is installed: `pip list | grep jarvis`
   - Verify imports in legacy backend
   - Check logs for initialization errors

3. **Memory Sync Issues**
   - Run memory migration: `POST /api/memory/migrate`
   - Check file permissions on data directories
   - Verify knowledge graph initialization

4. **GUI Won't Start**
   - Ensure PyQt6 is installed: `pip install PyQt6`
   - Check Python version compatibility
   - Verify new repo installation

### Debug Mode
Set environment variables for debugging:
```env
LOG_LEVEL=DEBUG
ENABLE_AGENT_LOGGING=true
```

### Logs
- Backend logs: Check console output
- GUI logs: Check GUI status bar
- Agent logs: Available through monitoring endpoints

## Performance Optimization

### Agent Management
- Adjust `MAX_CONCURRENT_AGENTS` based on system resources
- Use appropriate `AGENT_TIMEOUT` for your use case
- Monitor agent performance through metrics endpoints

### Memory Management
- Configure `MEMORY_LIMIT_MB` based on available RAM
- Use knowledge graph for persistent storage
- Regular memory cleanup through sync operations

### Monitoring
- Use `/api/monitoring/health` for system status
- Monitor `/api/monitoring/metrics` for performance
- Set up alerts based on health status

## Security Considerations

### Agent Security
- All agent actions are validated through security bridge
- Suspicious actions trigger additional validation
- Security events are logged and auditable

### API Security
- API key authentication available (set JARVIS_API_KEY)
- CORS configuration for web access
- Input validation on all endpoints

### Data Protection
- Sensitive data detection in agent contexts
- Secure credential storage using OS keyring
- Audit trails for all security events

## Future Enhancements

### Planned Features
- Additional agent types (specialized domains)
- Enhanced collaboration modes
- Advanced workflow templates
- Real-time monitoring dashboard
- Mobile application support

### Integration Opportunities
- External tool integrations
- Cloud deployment options
- Enterprise security features
- Advanced analytics and reporting

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run integration tests to identify problems
3. Review logs for error details
4. Use diagnostics tab in GUI for API testing

## License

This project maintains the same license as the original Jarvis AI system.
