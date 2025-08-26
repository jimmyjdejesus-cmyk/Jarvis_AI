# J.A.R.V.I.S. Desktop Application

This repository contains the source code for the J.A.R.V.I.S. desktop application, providing a modern and intuitive graphical user interface for interacting with the J.A.R.V.I.S. agentic system.

## Architecture

The application is built using a hybrid architecture that combines a Python backend with a web-based frontend, packaged in a native desktop shell using Tauri.

-   **Backend:** A Python application using **FastAPI** provides a robust API and a **WebSocket** server for real-time communication. It is located in the `app/` directory.
-   **Frontend:** A **React** single-page application provides the user interface. The source code is in the `src-tauri/src/` directory.
-   **Desktop Shell:** **Tauri** is used to wrap the frontend and backend into a single, cross-platform desktop executable. Tauri configuration is in `src-tauri/tauri.conf.json`.

The Python backend is packaged into an executable using **PyInstaller** and launched by the Tauri application as a **sidecar** process. This creates a fully self-contained application with no need for the user to install Python or other dependencies separately.

## Features

-   **Multi-Pane UI:** A comprehensive layout for managing all aspects of J.A.R.V.I.S.
    -   **Chat Pane:** For direct interaction with the agent system.
    -   **Project Sidebar:** To organize conversations by project.
    -   **Workflow Visualization:** A real-time graph of the agent teams' workflow.
    -   **Log Viewer:** Direct view of the `agent.md` log file.
    -   **HITL Oracle:** A pane for viewing and responding to Human-in-the-Loop prompts.
-   **Real-Time Communication:** WebSockets ensure a responsive and interactive user experience.
-   **Cross-Platform:** Packaged to run on Windows, macOS, and Linux.

## Development Setup

To run the application in a development environment, you will need **Python 3.8+** with `pip`, and **Node.js** with `npm`.

### 1. Backend Setup

Clone the repository and navigate to the root directory.

Install the required Python packages:
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
pip install -r requirements.txt
```

### 2. Frontend Setup

Navigate to the frontend directory and install the required Node.js packages:
```bash
cd src-tauri
npm install
cd ..
curl -sSL https://raw.githubusercontent.com/jimmyjdejesus-cmyk/Jarvis_AI/main/scripts/installers/install-unix.sh | bash

# Windows: Download and run scripts/installers/install-windows.bat
```

### 3. Running in Development Mode

You will need two separate terminals to run the backend and frontend servers concurrently.

**Terminal 1: Run the Backend**
```bash
python app/main.py
```
The backend server will start on `http://127.0.0.1:8000`.

**Terminal 2: Run the Frontend**
```bash
cd src-tauri
npm run dev
```
This will start the Tauri development server, which will open a native window with the application running and connected to your local backend server. The window supports hot-reloading for both the frontend and backend.

## Building the Application

To build the final, self-contained executable for distribution, you can use the provided build script. This script automates the process of packaging the backend and bundling the full application.

**Prerequisites:**
- Ensure all development dependencies are installed (Python and Node packages).
- Ensure `pyinstaller` is installed (`pip install pyinstaller`).
- Ensure you have the Tauri CLI and its prerequisites installed (see the [official Tauri guide](https://tauri.app/v1/guides/getting-started/prerequisites/)).

**Run the build script:**
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
chmod +x build.sh
./build.sh
```

This script will:
1.  Package the Python backend into an executable using `build_backend.sh`.
2.  (Simulate) building the React frontend for production.
3.  (Simulate) bundling the application using Tauri.

The final packaged application will be located in `src-tauri/target/release/bundle/`.

---
*This project is under active development.*
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
