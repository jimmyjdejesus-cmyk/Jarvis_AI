# Jarvis AI Migration Guide

## Overview

This guide helps you migrate from the legacy Jarvis AI system to the new unified architecture. It preserves existing
functionality while adding advanced multi-agent capabilities.

## Pre-Migration Checklist

### 1. Backup Your Data
```bash
# Backup existing data
cp -r data/ data_backup/
cp -r logs/ logs_backup/
cp config.json config_backup.json
```

### 2. System Requirements
- Python 3.9+
- Ollama installed and running
- Sufficient disk space for new components
- Memory: 8GB+ recommended for multi-agent operations

### 3. Dependencies
```bash
# Install required packages
pip install PyQt6 psutil websocket-client
pip install -e "C:\Users\Student\Downloads\github_repos\jarvis-ai"
```

## Migration Steps

### Step 1: Configuration Migration

Run the configuration migration tool:
```bash
python C:\Users\Student\.cursor\Jarvis_AI\legacy\scripts\migrate_config.py
```

This will:
- Convert environment variables to unified config format
- Create `~/.jarvis/config.json`
- Generate `.env.template` for customization
- Preserve existing settings

### Step 2: Data Migration

#### Memory Data
```bash
# Start the backend
python -m uvicorn jarvis_core.server:build_app --factory --host 127.0.0.1 --port 8000
```

Note: The original `legacy/` runtime has been archived to `archive/legacy`.
If you need to run the legacy system for migration testing, restore it first:

```bash
# git mv archive/legacy legacy
# git commit -m "restore legacy for local migration testing"
# uvicorn legacy.app.main:app --host 127.0.0.1 --port 8000
```

In another terminal, run the migration:

```bash
curl -X POST http://127.0.0.1:8000/api/memory/migrate
```

#### Knowledge Graph
```bash
# Sync knowledge to legacy format
curl -X POST http://127.0.0.1:8000/api/memory/sync/to-legacy

# Load legacy data into new system
curl -X POST http://127.0.0.1:8000/api/memory/sync/from-legacy
```

### Step 3: Agent Setup

#### Initialize Agents
The system will automatically create agents when first used. You can also manually initialize:

```bash
# Check available agents
curl http://127.0.0.1:8000/api/agents

# Test agent execution
curl -X POST http://127.0.0.1:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "research", "objective": "Test migration"}'
```

### Step 4: Workflow Migration

#### Legacy Workflows
Existing workflows will continue to work. New workflow capabilities are available through:

```bash
# Check workflow capabilities
curl http://127.0.0.1:8000/api/workflows/capabilities

# Execute new workflow
curl -X POST http://127.0.0.1:8000/api/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{"workflow_type": "research", "parameters": {"query": "test"}}'
```

### Step 5: Security Configuration

#### Security Audit
```bash
# Run security audit
curl -X POST http://127.0.0.1:8000/api/security/audit

# Check security stats
curl http://127.0.0.1:8000/api/security/stats
```

#### API Security
If you had API key authentication enabled:
```bash
# Set API key
export JARVIS_API_KEY="your-api-key"

# Or add to .env file
echo "JARVIS_API_KEY=your-api-key" >> .env
```

## Post-Migration Verification

### 1. Run Integration Tests
```bash
python C:\Users\Student\.cursor\Jarvis_AI\legacy\scripts\test_integration.py
```

### 2. Test GUI
```bash
python C:\Users\Student\.cursor\Jarvis_AI\legacy\scripts\run_new_gui.py
```

### 3. Verify API Endpoints
```bash
# Health check
curl http://127.0.0.1:8000/health

# Models
curl http://127.0.0.1:8000/api/models

# Chat
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Configuration Changes

### Environment Variables
The following environment variables are now supported:

#### Ollama Configuration
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
OLLAMA_TIMEOUT=120
OLLAMA_MAX_TOKENS=4096
OLLAMA_TEMPERATURE=0.7
```

#### Agent Configuration
```env
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT=300
MEMORY_LIMIT_MB=8192
ENABLE_AGENT_LOGGING=true
COLLABORATION_ENABLED=true
```

#### API Configuration
```env
API_HOST=127.0.0.1
API_PORT=8000
ENABLE_CORS=true
ENABLE_AUTH=false
```

### Config File Structure
The new config file (`~/.jarvis/config.json`) includes:

```json
{
  "ollama": { ... },
  "agents": { ... },
  "research": { ... },
  "gui": { ... },
  "api": { ... },
  "database": { ... }
}
```

## New Features Available

### 1. Multi-Agent System
- **Research Agent**: Automated literature search and analysis
- **Coding Agent**: Code generation, analysis, and debugging
- **Curiosity Agent**: Creative exploration and hypothesis generation
- **Benchmark Agent**: Testing and performance evaluation

### 2. Advanced Collaboration
- **Parallel Processing**: Multiple agents working simultaneously
- **Sequential Workflows**: Agents passing results to each other
- **Hierarchical Coordination**: Lead agent coordinating others

### 3. Enhanced Memory
- **Conversation Memory**: Persistent chat history
- **Knowledge Graph**: Structured knowledge storage
- **Memory Bridging**: Seamless data migration

### 4. Security & Monitoring
- **Real-time Security**: Action validation and auditing
- **Performance Monitoring**: System metrics and health checks
- **Security Events**: Comprehensive security logging

### 5. Research Pipeline
- **Literature Search**: Automated paper discovery
- **Analysis Tools**: Advanced research capabilities
- **Knowledge Integration**: Automatic knowledge graph updates

## Troubleshooting Migration Issues

### Common Problems

#### 1. Import Errors
```bash
# Ensure new repo is installed
pip install -e "C:\Users\Student\Downloads\github_repos\jarvis-ai"

# Check Python path
python -c "import jarvis; print(jarvis.__file__)"
```

#### 2. Configuration Issues
```bash
# Re-run migration
python C:\Users\Student\.cursor\Jarvis_AI\legacy\scripts\migrate_config.py

# Check config file
cat ~/.jarvis/config.json
```

#### 3. Agent Initialization Failures
```bash
# Check agent manager status
curl http://127.0.0.1:8000/api/agents

# Check logs for errors
tail -f logs/jarvis.log
```

#### 4. Memory Sync Issues
```bash
# Force memory sync
curl -X POST http://127.0.0.1:8000/api/memory/migrate

# Check memory stats
curl http://127.0.0.1:8000/api/memory/stats
```

### Debug Mode
Enable debug logging:
```env
LOG_LEVEL=DEBUG
ENABLE_AGENT_LOGGING=true
```

### Rollback Procedure
If migration fails:

1. Stop all services
2. Restore from backup:
   ```bash
   cp -r data_backup/ data/
   cp -r logs_backup/ logs/
   cp config_backup.json config.json
   ```
3. Revert to legacy mode
4. Investigate issues before retrying

## Performance Considerations

### Resource Requirements
- **CPU**: Multi-core recommended for agent parallelism
- **Memory**: 8GB+ for multi-agent operations
- **Storage**: Additional space for new components
- **Network**: Stable connection for Ollama and web searches

### Optimization Tips
1. Adjust `MAX_CONCURRENT_AGENTS` based on system resources
2. Use appropriate `AGENT_TIMEOUT` values
3. Monitor system metrics through `/api/monitoring/health`
4. Regular memory cleanup through sync operations

## Support and Help

### Getting Help
1. Check the troubleshooting section
2. Run integration tests to identify issues
3. Review system logs for error details
4. Use the diagnostics tab in the GUI

### Documentation
- **Architecture**: `UNIFIED_ARCHITECTURE.md`
- **API Reference**: Available through `/docs` endpoint
- **Configuration**: `~/.jarvis/config.json` comments

### Community
- Report issues through the project repository
- Share configurations and optimizations
- Contribute to the agent ecosystem

## Migration Checklist

- [ ] Backup existing data
- [ ] Install new dependencies
- [ ] Run configuration migration
- [ ] Start backend services
- [ ] Migrate memory data
- [ ] Test agent functionality
- [ ] Verify workflow execution
- [ ] Run security audit
- [ ] Test GUI application
- [ ] Run integration tests
- [ ] Update documentation
- [ ] Train users on new features

## Success Criteria

Migration is successful when:
- [ ] All integration tests pass
- [ ] GUI launches without errors
- [ ] Agents can execute tasks
- [ ] Memory data is accessible
- [ ] Workflows execute successfully
- [ ] Security systems are active
- [ ] Monitoring shows healthy status
- [ ] Legacy functionality is preserved

## Next Steps

After successful migration:
1. Explore new agent capabilities
2. Set up monitoring dashboards
3. Configure security policies
4. Train team on new features
5. Plan advanced workflows
6. Consider additional integrations

Congratulations on successfully migrating to the unified Jarvis AI system!
