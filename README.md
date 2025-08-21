<<<<<<< HEAD
# Jarvis AI

A privacy-first modular AI development assistant with comprehensive deployment and distribution capabilities.

## 🚀 Quick Start

### Installation Methods

#### 1. Pip Package (Recommended)
```bash
pip install jarvis-ai
jarvis run
```

#### 2. Docker Container
```bash
docker-compose up -d
# Or build from source
docker build -t jarvis-ai .
docker run -p 8501:8501 jarvis-ai
```

#### 3. One-Click Installer
```bash
curl -sSL https://raw.githubusercontent.com/jimmyjdejesus-cmyk/Jarvis_AI/main/scripts/installers/install-unix.sh | bash

# Windows: Download and run scripts/installers/install-windows.bat
```

### Configuration

```bash
# Initialize configuration
jarvis config --init

# Validate settings
jarvis config --validate

# Show current config
jarvis config --show
```

### Environment Variables (CI/CD Ready)
```bash
# General settings
export JARVIS_DEBUG_MODE=true
export JARVIS_V2_ENABLED=true

# Lang Ecosystem Integration
export LANGSMITH_API_KEY=your_key
export JARVIS_LANGSMITH_ENABLED=true
export LANGGRAPH_PLATFORM_API_KEY=your_platform_key
```

## 📋 Features

### Deployment & Distribution ✨
- **Python Package**: Install via `pip install jarvis-ai`
- **Docker Support**: Multi-stage builds with health checks
- **One-Click Installers**: For non-technical users
- **YAML Configuration**: Hierarchical settings with validation
- **Environment Overrides**: Perfect for CI/CD deployments
- **UI Settings Manager**: Web-based configuration interface

### Lang Ecosystem Integration 🤖
- **LangSmith**: Production monitoring and tracing
- **LangGraph Platform**: Team collaboration and agent sharing
- **LangChain Tools**: Standardized plugin development
- **Deployment Telemetry**: Performance and error tracking

## Repository Structure

This repository is organized as follows:

### Legacy Code
All previous implementation of the Jarvis AI assistant has been archived in the `legacy/` folder. This includes:
# Jarvis AI

A privacy-first modular AI development assistant with comprehensive deployment and distribution capabilities.

## 🚀 Quick Start

### Installation Methods

#### 1. Pip Package (Recommended)
```bash
pip install jarvis-ai
jarvis run
```

#### 2. Docker Container
```bash
docker-compose up -d
# Or build from source
docker build -t jarvis-ai .
docker run -p 8501:8501 jarvis-ai
```

#### 3. One-Click Installer
```bash
# Unix/Linux/macOS
curl -sSL https://raw.githubusercontent.com/jimmyjdejesus-cmyk/Jarvis_AI/main/scripts/installers/install-unix.sh | bash

# Windows: Download and run scripts/installers/install-windows.bat
```

### Configuration
```bash
# Initialize configuration
jarvis config --init

# Validate settings
jarvis config --validate

# Show current config
jarvis config --show
```

### Environment Variables (CI/CD Ready)
```bash
# General settings
export JARVIS_DEBUG_MODE=true
export JARVIS_V2_ENABLED=true
- Original Python application files
- Database implementation
- UI components
- Agent implementation
- Authentication system
- Tools and plugins
- Documentation

### New Development
The root directory now serves as the starting point for the next phase of development. Future implementations will be built here while preserving the legacy code for reference.

## 📖 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Comprehensive deployment and distribution documentation
- **[Lang Ecosystem Integration](docs/LANG_ECOSYSTEM_ISSUE_INTEGRATION.md)**: Integration with LangChain, LangGraph, and LangSmith
- **Legacy Documentation**: Available in the `legacy/` folder

## 🔧 Development

```bash
# Clone repository
git clone https://github.com/jimmyjdejesus-cmyk/Jarvis_AI.git
cd Jarvis_AI

# Install in development mode
pip install -e .

# Validate deployment
./scripts/validate_deployment.sh
```

## Getting Started

## Quick Demo Script
.\venv\Scripts\python.exe -m streamlit run ui_demo.py

To work with this repository:

1. **For End Users**: Use pip installation or one-click installer
2. **For Developers**: Build new features in the root directory
3. **Legacy Reference**: Explore the `legacy/` folder for previous implementation

## Completed Features 

## Coding Tools
Code explanation generation: Added context-aware explanations for code completions that adapt to user's communication style and domain specialization
Completion rationale display: Implemented detailed reasoning display showing confidence factors, pattern recognition, and decision logic behind AI suggestions
Knowledge source attribution: Added comprehensive source tracking including user interaction history, domain knowledge, and model confidence factors

Learning rate adjustment: Implemented 4-tier learning system (Conservative, Moderate, Adaptive, Aggressive) controlling how quickly AI adapts to user preferences
Domain specialization settings: Added 8 specialized domains (Web Development, Data Science, DevOps, etc.) with tailored response patterns
Style preference configuration: Implemented 5 communication styles (Concise, Detailed, Tutorial, Professional, Casual) affecting all AI interactions

The implementation follows the documented Lang ecosystem approach:
LangChain Memory: Created PersonalizationMemory class for persistent user learning and adaptation
LangGraph workflows: Enhanced existing workflow with personalization initialization, explanation generation, and feedback processing nodes
LangGraphUI visualization: Added interactive personalized workflow views with user context panels and quick feedback collection
Enhanced Code Intelligence: Integrated personalization engine that generates contextually relevant suggestions

#UI Enhancements
learning_rate = st.selectbox("AI Learning Rate", ["Conservative", "Moderate", "Adaptive", "Aggressive"])
domain = st.selectbox("Domain Specialization", ["General", "Web Development", "Data Science", ...])
style = st.selectbox("Communication Style", ["Concise", "Detailed", "Tutorial", ...])

## Contact

For questions or support, please contact the repository owner.
=======
# Jarvis AI – Local, Visual Agent (Finalized)

This is a **self‑contained local build** of Jarvis with:
- A **dynamic agent** framework (no external dependencies) you can extend with tools.
- A **native desktop UI** (Tkinter) for casual chat or prompt‑engineering.
- A **visual workflow panel** that shows each step (planning → research → analysis) and lets you click nodes to inspect details.
- **Session persistence** to disk (chat folders) under `data/sessions/`.

## Run

```bash
# Desktop app
python -m jarvis --gui

# CLI
python -m jarvis "Refactor database.py to improve performance"
```

## Sessions (chat folders)

Each run is persisted to `data/sessions/<id>/` with:
- `session.json` (metadata)
- `log.jsonl` (one JSON object per run with your objective and step outputs)

From the UI: **File → New Session** or **File → Load Session** to manage sessions.

## Structure

```
jarvis/
  __init__.py
  __main__.py
  dynamic_agents/
    __init__.py
    factory.py
    default_tools.py
  persistence/
    session.py
  ui/
    __init__.py
    gui.py
README.md
```

## Extending

- Replace the stub tools in `dynamic_agents/default_tools.py` with real tools: Ollama calls, RAG retrieval, Notion/OneNote/Gmail/Calendar, web search, etc.
- The UI’s graph canvas (`ui/gui.py`) is ready for more nodes/edges; add confirm gates or a timeline as needed.
- Use `persistence/session.py` to store additional artifacts (diffs, attachments, summaries).

## Notes

- This build is deliberately dependency‑light so you can run it anywhere.
- When you’re ready, swap the internal loop for a LangGraph graph and keep the UI the same—only the tools and agent driver change.
>>>>>>> 8482792 (Initial commit)
