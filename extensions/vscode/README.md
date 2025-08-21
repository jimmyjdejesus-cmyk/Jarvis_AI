# Jarvis AI VS Code Extension

This extension connects VS Code to the Jarvis AI backend over WebSockets to provide:

- **Inline suggestions** as you type
- **Repository context streaming** to supply the AI with project information
- **Autonomous debugging prompts** to help resolve runtime errors

## Development

1. Ensure the Python backend has the `websockets` package installed:
   ```bash
   pip install websockets
   python vscode_integration.py --server
   ```
   The server listens on `ws://localhost:8765` by default.

2. Install extension dependencies and compile:
   ```bash
   cd extensions/vscode
   npm install
   npm run compile
   ```

3. Package the extension (requires `vsce`):
   ```bash
   npm run package
   # produces jarvis-vscode-0.1.0.vsix
   ```

4. Install the generated package:
   ```bash
   code --install-extension jarvis-vscode-0.1.0.vsix
   ```

## Usage

- Start typing in any file to receive inline suggestions.
- Run `Jarvis: Stream Repository Context` from the command palette to send project data to Jarvis.
- Run `Jarvis: Debug Error` to receive debugging tips for a provided error message.
