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
```bash
pip install -r requirements.txt
```

### 2. Frontend Setup

Navigate to the frontend directory and install the required Node.js packages:
```bash
cd src-tauri
npm install
cd ..
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
