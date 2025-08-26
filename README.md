# Jarvis AI - Multi-Agent Orchestrator

A powerful desktop application for orchestrating AI agents with visual flow editing, built with Tauri, React, and React Flow.

## Features

- **Galaxy Model Visualization**: Hierarchical view of crews and agents with 3D-like navigation
- **Multi-dimensional Relationship Tracing**: Visual connections showing data flow, control, and dependencies
- **Rich Desktop Experience**: 
  - Resizable panes
  - Multiple chat windows
  - Project management
  - Crew and agent organization
- **Three View Modes**:
  - Galaxy View: High-level overview of all crews
  - Crew View: Detailed view of a specific crew and its agents
  - Agent View: Focus on individual agent configuration
- **Chat Interface**:
  - Multiple chat modes (Chat, Research, Agent)
  - Resizable chat panes
  - Project-based organization

## Migration from vis-network-react to react-flow

This project has been migrated from `vis-network-react` to `react-flow` for better performance, more features, and active maintenance.

### Key Improvements:
- Better performance with large graphs
- Built-in controls for zoom, pan, and minimap
- More customization options
- Better TypeScript support
- Active community and regular updates

## Installation

1. **Install Node.js dependencies:**
```bash
npm install
```

2. **Install Rust and Tauri CLI (if not already installed):**
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Tauri CLI
npm install -g @tauri-apps/cli
```

3. **Run the development server:**
```bash
# Run the web development server
npm run dev

# Or run with Tauri (desktop app)
npm run tauri:dev
```

4. **Build for production:**
```bash
# Build web assets
npm run build

# Build desktop app
npm run tauri:build
```

## Project Structure

```
jarvis-ai/
├── src/                    # React frontend source
│   ├── components/         # React components
│   │   ├── FlowCanvas.tsx  # Main React Flow canvas
│   │   ├── Sidebar.tsx     # Project management sidebar
│   │   └── ChatPanel.tsx   # Chat interface
│   ├── store/             # State management (Zustand)
│   ├── styles/            # CSS styles
│   └── types/             # TypeScript type definitions
├── src-tauri/             # Tauri backend (Rust)
├── index.html             # Entry HTML
├── package.json           # Node dependencies
└── vite.config.ts         # Vite configuration
```

## Usage

### Creating a New Project
1. Click "New Project" in the sidebar
2. Name your project
3. Start adding crews and agents

### Working with Crews
1. Switch to Galaxy View to see all crews
2. Click on a crew to enter Crew View
3. Add agents by clicking the "+" button
4. Connect agents by dragging from one to another

### Managing Agents
1. Click on an agent to select it
2. Configure agent properties in the sidebar
3. View agent status and capabilities
4. Create connections to other agents

### Using the Chat Interface
1. Click "New Chat" to start a conversation
2. Switch between Chat, Research, and Agent modes
3. Resize panes by dragging the dividers
4. Add or remove chat panes as needed

## Technologies Used

- **Frontend**: React 18, TypeScript, Vite
- **Desktop**: Tauri (Rust)
- **Flow Visualization**: React Flow 11
- **State Management**: Zustand
- **Styling**: Tailwind CSS, CSS Modules
- **UI Components**: Lucide React (icons), Framer Motion (animations)
- **Utilities**: UUID, D3.js (for Galaxy visualization)

## Development

### Adding New Agent Types
Edit `src/types/index.ts` and add your agent type to the `Agent` interface.

### Customizing the Galaxy View
Modify `src/components/FlowCanvas.tsx` and adjust the `renderGalaxyView` function.

### Adding New Chat Modes
Update the `ChatMode` type in `src/types/index.ts` and modify `src/components/ChatPanel.tsx`.

## Troubleshooting

If you encounter TypeScript errors, ensure all dependencies are installed:
```bash
npm install
```

If Tauri doesn't start, ensure Rust is properly installed:
```bash
rustc --version
cargo --version
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
