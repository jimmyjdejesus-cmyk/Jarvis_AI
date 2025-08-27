# Jarvis AI Deployment & Distribution Guide

This guide covers all deployment and distribution options for Jarvis AI, including the new Lang ecosystem integration features.

## 📦 Installation Methods

### 1. Pip Package Installation

Install Jarvis AI as a Python package:

```bash
# Basic installation
pip install jarvis-ai

# With enhanced features
pip install jarvis-ai[enhanced]

# With cloud integration
pip install jarvis-ai[cloud]

# Development installation (from source)
git clone https://github.com/jimmyjdejesus-cmyk/Jarvis_AI.git
cd Jarvis_AI
pip install -e .
```

**Usage after installation:**
```bash
# Start the application
jarvis run

# Initialize configuration
jarvis config --init

# Show version and status
jarvis version

# Setup (equivalent to legacy setup_enhanced.py)
jarvis-setup
```

### 2. Docker Container Deployment

For consistent environments across different systems:

```bash
# Build the container
docker build -t jarvis-ai .

# Run the container
docker run -p 8501:8501 jarvis-ai

# Or use docker-compose for full stack with Ollama
docker-compose up -d
```

**Docker Environment Variables:**
```bash
docker run -p 8501:8501 \
  -e JARVIS_DEBUG_MODE=false \
  -e LANGSMITH_API_KEY=your_key_here \
  -e JARVIS_LANGSMITH_ENABLED=true \
  -v jarvis_data:/app/data \
  jarvis-ai
```

To configure Neo4j, store credentials in the OS keyring using ``keyring``:

```bash
python -m keyring set jarvis NEO4J_URI bolt://localhost:7687
python -m keyring set jarvis NEO4J_USER neo4j
python -m keyring set jarvis NEO4J_PASSWORD test
```

Rotate these secrets regularly and update the keyring entries accordingly.
The desktop application also provides fields in its settings panel where users
can enter Neo4j credentials at runtime.

### 3. One-Click Installer

For non-technical users:

**Unix/Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/jimmyjdejesus-cmyk/Jarvis_AI/main/scripts/installers/install-unix.sh | bash
```

**Windows:**
Download and run `scripts/installers/install-windows.bat`

The installer will:
- Check system requirements
- Install Python if needed
- Create virtual environment
- Download and install Jarvis AI
- Initialize configuration
- Create desktop shortcuts

## ⚙️ Configuration Management

### YAML-Based Configuration

Jarvis AI uses a hierarchical YAML configuration system located at `config/config.yaml`:

```yaml
# Basic configuration
app_name: "Jarvis AI"
version: "2.0.0"
debug_mode: false
data_directory: "data"
logs_directory: "logs"

# Lang Ecosystem Integration (NEW)
lang_ecosystem:
  # LangSmith for tracing and monitoring
  langsmith:
    enabled: true
    api_key: ""  # Set via LANGSMITH_API_KEY env var
    project_name: "jarvis-ai"
    trace_deployments: true
    
  # LangGraph Platform for team collaboration
  langgraph_platform:
    enabled: false
    api_key: ""  # Set via LANGGRAPH_PLATFORM_API_KEY env var
    workspace_id: ""
    deployment_environment: "production"
    
  # Deployment monitoring
  deployment:
    enable_telemetry: true
    performance_tracking: true
    error_tracking: true
```

### UI-Based Settings Manager

Access the web-based configuration interface:

1. Start Jarvis AI: `jarvis run`
2. Navigate to the Settings tab in the sidebar
3. Configure settings through the intuitive interface
4. Changes are saved to `config/config.yaml`

Features:
- Real-time configuration validation
- Environment variable integration
- Deployment status monitoring
- Lang ecosystem configuration

### Environment Variable Overrides

Perfect for CI/CD and containerized deployments:

#### Jarvis-Specific Variables:
```bash
# General settings
export JARVIS_DEBUG_MODE=true
export JARVIS_DATA_DIRECTORY=/custom/data
export JARVIS_LOGS_DIRECTORY=/custom/logs

# V2 Architecture
export JARVIS_V2_ENABLED=true
export JARVIS_V2_EXPERT_MODEL=llama3.1

# Lang Ecosystem
export JARVIS_LANGSMITH_ENABLED=true
export JARVIS_LANGSMITH_PROJECT_NAME=my-project
export JARVIS_LANGGRAPH_PLATFORM_ENABLED=true
export JARVIS_DEPLOYMENT_TELEMETRY=true
```

#### Standard Lang Ecosystem Variables:
```bash
# LangSmith (standard variables)
export LANGSMITH_API_KEY=your_api_key
export LANGSMITH_PROJECT=jarvis-ai

# LangGraph Platform
export LANGGRAPH_PLATFORM_API_KEY=your_platform_key

# LangChain
export LANGCHAIN_VERBOSE=true
```

## 🚀 Deployment Patterns

### 1. Local Development

```bash
# Clone and setup
git clone https://github.com/jimmyjdejesus-cmyk/Jarvis_AI.git
cd Jarvis_AI
pip install -e .

# Initialize configuration
jarvis config --init

# Start development server
jarvis run --port 8501
```

### 2. Production Deployment

#### Option A: Docker Compose (Recommended)

```bash
# Production docker-compose.yml
version: '3.8'
services:
  jarvis-ai:
    image: jarvis-ai:latest
    ports:
      - "8501:8501"
    environment:
      - JARVIS_DEBUG_MODE=false
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
      - JARVIS_LANGSMITH_ENABLED=true
    volumes:
      - jarvis_data:/app/data
      - jarvis_logs:/app/logs
    restart: unless-stopped
```

#### Option B: Traditional Server

```bash
# On production server
pip install jarvis-ai
jarvis config --init

# Edit production configuration
nano config/config.yaml

# Start with production settings
JARVIS_DEBUG_MODE=false jarvis run --host 0.0.0.0 --port 8501
```

### 3. CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Deploy Jarvis AI

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -e .
    
    - name: Run tests
      run: pytest
      
    - name: Deploy to production
      env:
        JARVIS_DEBUG_MODE: false
        LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
        JARVIS_LANGSMITH_ENABLED: true
      run: |
        jarvis config --validate
        # Deploy to your infrastructure
```

## 🔍 Lang Ecosystem Integration

### LangSmith Integration

Automatic tracing and monitoring for production deployments:

```python
# Automatically enabled when LANGSMITH_API_KEY is set
import os
os.environ["LANGSMITH_API_KEY"] = "your_key"
os.environ["LANGSMITH_PROJECT"] = "jarvis-ai-production"

# Configuration
lang_ecosystem:
  langsmith:
    enabled: true
    project_name: "jarvis-ai-production"
    trace_deployments: true
    trace_performance: true
```

Features:
- Automatic deployment monitoring
- Installation success/failure tracking
- Performance metrics for deployed agents
- Error tracking and debugging

### LangGraph Platform Integration

Team collaboration and agent sharing:

```yaml
lang_ecosystem:
  langgraph_platform:
    enabled: true
    workspace_id: "your_workspace"
    deployment_environment: "production"
    enable_sharing: true
    enable_collaboration: true
```

Features:
- Agent sharing across teams
- Centralized deployment management
- Scaling infrastructure for long-running workflows
- Team collaboration tools

## 🔧 Migration from Legacy Setup

If you're upgrading from the legacy setup system:

1. **Existing installations** continue to work unchanged
2. **New installations** should use the pip package: `pip install jarvis-ai`
3. **Configuration** is backward compatible
4. **Enhanced setup** is available via `jarvis-setup` command

### Migration Steps:

```bash
# 1. Backup existing configuration
cp config/config.yaml config/config.yaml.backup

# 2. Install new package version
pip install jarvis-ai

# 3. Update configuration with Lang ecosystem settings
jarvis config --init  # This merges with existing config

# 4. Validate new configuration
jarvis config --validate

# 5. Start with new CLI
jarvis run
```

## 📊 Monitoring and Telemetry

### Deployment Monitoring

Built-in monitoring for production deployments:

```yaml
lang_ecosystem:
  deployment:
    enable_telemetry: true
    performance_tracking: true
    error_tracking: true
    deployment_notifications: true
    notification_webhook: "https://your-webhook-url"
```

### Health Checks

```bash
# Docker health check
curl -f http://localhost:8501/_stcore/health

# API health check
curl http://localhost:8501/api/health

# CLI status check
jarvis version
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -e .[enhanced]
   ```

2. **Configuration Issues**: Validate configuration
   ```bash
   jarvis config --validate
   ```

3. **Docker Issues**: Check container logs
   ```bash
   docker logs jarvis-ai
   ```

4. **Environment Variables**: Check environment setup
   ```bash
   jarvis config --show
   ```

### Support:

- **Documentation**: `/docs` directory
- **Issues**: GitHub Issues
- **Configuration**: Use the UI-based settings manager
- **Logs**: Check `logs/` directory for detailed error information

## 🚦 Next Steps

1. Choose your deployment method
2. Configure Lang ecosystem integration
3. Set up monitoring and telemetry
4. Configure CI/CD pipeline
5. Scale your deployment as needed

For more detailed information, see the individual configuration files and documentation in the `/docs` directory.