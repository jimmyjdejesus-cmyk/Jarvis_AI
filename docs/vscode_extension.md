# VS Code Extension

This extension connects the Jarvis AI backend to Visual Studio Code.

## Installation

1. **Install the Python backend dependencies**:
   ```bash
   pip install websockets
   ```
2. **Run the backend server**:
   ```bash
   python -m integrations.vscode --server
   ```
   The server listens on `ws://localhost:8765` by default.
3. **Install the VS Code extension**:
   ```bash
   cd extensions/vscode
   npm install
   npm run package
   code --install-extension jarvis-vscode-0.1.0.vsix
   ```

## Usage

- Start typing in a file to receive inline suggestions.
- Use the command palette to stream repository context or trigger debugging help.
- Real-time suggestions and debugging leverage Jarvis's repository indexer for project-aware assistance.
