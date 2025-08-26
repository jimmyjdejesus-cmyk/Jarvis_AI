# Jarvis AI

J.A.R.V.I.S. is a powerful, privacy-first, and modular platform for developing and orchestrating advanced AI agents. It is designed with a microservices architecture to be scalable, extensible, and robust.

## 🚀 Quick Start

The recommended way to run Jarvis AI is by using the Streamlit-based web interface.

### 1. Prerequisites

*   Python 3.8+
*   Docker and Docker Compose (optional, for Docker-based setup)

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jimmyjdejesus-cmyk/Jarvis_AI.git
    cd Jarvis_AI
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file to add any necessary API keys (e.g., for LangSmith).

### 3. Running the Application

You can run the application using the `jarvis` command:

```bash
python -m jarvis_ai.cli run
```

This will start the Streamlit web interface, which will be available at `http://localhost:8501`.

Alternatively, you can use the launcher script:

```bash
python launcher.py
```

This will give you a menu of options, including the web UI, desktop apps, and CLI.

### 4. Docker-based Setup

If you prefer to use Docker, you can run the entire platform with Docker Compose:

```bash
docker-compose up -d --build
```

The API will be available at `http://localhost:8000`.

## 📋 Features

*   **Streamlit Web Interface:** A modern and intuitive web interface for interacting with the AI.
*   **Ollama Integration:** Run local, open-source language models.
*   **Lang Ecosystem Integration:** Built-in support for LangChain, LangGraph, and LangSmith.
*   **Plugin System:** Extend the functionality of the application with custom plugins.
*   **Custom Workflows:** Create your own custom workflows to automate complex tasks.
*   **Authentication:** User and admin roles with an admin panel for management.
*   **Security and Privacy:** Local processing, encrypted data storage, and audit logs.

## 📖 Documentation

*   **[Integration Guide](docs/INTEGRATION_GUIDE.md)**: A guide to integrating Jarvis with other systems.
*   **[Customization Guide](docs/CUSTOMIZATION_GUIDE.md)**: A guide to customizing and extending the application.
*   **[Legacy Applications](docs/LEGACY.md)**: Information about the older Tkinter and Tauri desktop applications.

## 🔧 Development

To run the application in a development environment, follow the installation steps above. You can then run the backend and frontend servers separately.

*   **Backend (FastAPI):**
    ```bash
    python app/main.py
    ```

*   **Frontend (Streamlit):**
    ```bash
    streamlit run jarvis_chat.py
    ```

---
*This project is under active development.*
