# 🧠 Enhanced Jarvis AI - Cerebro Galaxy Model

A revolutionary AI system featuring a **Cerebro-centric galaxy visualization** where a central meta-agent dynamically spawns multi-agent orchestrators based on natural language conversations.

## 🌌 What Makes This Special

### **Cerebro Galaxy Architecture**
- **🧠 Cerebro** - Central meta-agent that processes your natural language
- **🎭 Orchestrators** - Multi-agent systems spawned dynamically by Cerebro  
- **🤖 Agents** - Individual AI agents within orchestrators
- **⚡ Tasks** - Specific executions and Monte Carlo simulations

### **Interactive Experience**
- **Chat with Cerebro** → Watch it think and spawn orchestrators
- **Navigate the Galaxy** → Click nodes to zoom through levels
- **Real-time Updates** → See live animations as agents work
- **Professional UI** → Stunning visual effects and responsive design

## 🚀 Quick Start

### **Option 1: Full System (Recommended)**
```bash
# Windows users - just double-click:
start_jarvis.bat

# Or run manually:
python start_jarvis_enhanced.py
```

### **Option 2: Backend + Frontend Separately**
```bash
# Terminal 1 - Start Backend:
start_backend.bat
# or: python start_backend_only.py

# Terminal 2 - Start Frontend:
cd src-tauri
npm run dev
```

### Environment Variables

The backend reads Neo4j connection details from the environment. Tests mock the
database, but you can override defaults by setting:

| Variable         | Default                    |
|------------------|----------------------------|
| `NEO4J_URI`      | `bolt://localhost:7687`    |
| `NEO4J_USER`     | `neo4j`                    |
| `NEO4J_PASSWORD` | `test`                     |

These values allow the application or tests to connect to a real Neo4j instance
when desired.

### **Option 3: Manual Setup**
```bash
# 1. Install Python dependencies
# FastAPI 0.111.x is compatible with Pydantic 2.7+
pip install fastapi==0.111.0 uvicorn websockets redis "pydantic>=2.7,<3" pyjwt python-multipart

# 2. Start backend
cd app
python main.py

# 3. Install and start frontend (new terminal)
cd src-tauri
npm install --legacy-peer-deps
npm run dev

# 4. Open browser to http://localhost:5173
```

## 🔐 Authentication


The backend exposes an OAuth2 password flow and returns JWTs for authenticated
requests. Retrieve a token via the `/token` endpoint:

```bash
curl -X POST -F "username=admin" -F "password=adminpass" http://localhost:8000/token
```

Use the token in the `Authorization` header when calling protected routes:
`Authorization: Bearer <token>`.

Sample in-memory users:

| Username | Password   | Role  |
|----------|------------|-------|
| admin    | adminpass  | admin |
| user     | userpass   | user  |

## Endpoints like `/api/logs` require the `admin` role.
The backend secures selected endpoints using OAuth2 bearer tokens with JWT.

1. Request a token:

   ```bash
   curl -X POST -F "username=alice" -F "password=secret" http://localhost:8000/token
   ```

2. Use the token:

   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/logs
   ```

Endpoints such as `/api/logs` require the `admin` role and return `403` for unauthorized users.


## 🎯 What You'll See

### **🌌 Galaxy View**
- **Cerebro at center** with animated neural network
- **Orchestrators orbiting** around Cerebro
- **Agents within orchestrators** with task satellites
- **Real-time status indicators** and animations

### **💬 Interactive Chat**
- Type messages to activate Cerebro
- Watch thinking animations and orchestrator spawning
- See real-time galaxy updates as you chat

### **🎮 Navigation**
- **Click Cerebro** → Zoom to orchestrator level
- **Click orchestrators** → See individual agents  
- **Click agents** → View task simulations
- **Use back button** → Navigate up levels

## 🔧 Troubleshooting

### **"Backend not connected" Error**
1. **Check backend console** - Look for separate window showing FastAPI logs
2. **Manual start** - Run `start_backend.bat` or `python start_backend_only.py`
3. **Verify port 8000** - Visit http://localhost:8000 to test backend
4. **Refresh browser** - Reload http://localhost:5173

### **Galaxy Not Loading**
1. **Hard refresh** - Press Ctrl+F5 or Cmd+Shift+R
2. **Check console** - Open browser dev tools (F12) for errors
3. **Verify build** - Look for errors in frontend console window

### **Dependencies Issues**
1. **Run as Administrator** - Right-click .bat files → "Run as administrator"
2. **Manual npm install** - `cd src-tauri && npm install --legacy-peer-deps`
3. **Check Node.js** - Ensure Node.js 16+ is installed

## 📁 Project Structure

```
Enhanced-Jarvis-AI/
├── 🚀 start_jarvis.bat              # Windows launcher
├── 🐍 start_jarvis_enhanced.py      # Cross-platform launcher  
├── 🪟 start_jarvis_enhanced_windows.py # Windows-optimized launcher
├── 🔧 start_backend.bat             # Backend-only launcher
├── 📱 app/                          # FastAPI backend
│   └── main.py                      # Backend server
├── 🎨 src-tauri/                    # React frontend
│   ├── src/components/              # UI components
│   │   ├── GalaxyVisualization.jsx  # Cerebro galaxy model
│   │   ├── ChatPane.jsx             # Interactive chat
│   │   └── WorkflowPane.jsx         # Main workflow view
│   └── src/styles.css               # Galaxy animations & styling
└── ⚙️ config/                       # Configuration files
```

## 🎉 Success Indicators

You'll know everything is working when you see:

✅ **Backend Console**: `INFO: Uvicorn running on http://0.0.0.0:8000`  
✅ **Frontend Console**: `Local: http://localhost:5173/`  
✅ **Browser**: Cerebro galaxy with animated neural network  
✅ **Chat**: Messages trigger Cerebro thinking animations  
✅ **Status**: "Connected" instead of "Backend not connected"  

## 🌟 Features

- **🧠 Cerebro Meta-Agent** - Central intelligence processing natural language
- **🎭 Dynamic Orchestrators** - Multi-agent systems spawned on demand
- **🌌 Galaxy Navigation** - Interactive zoom through system levels
- **💬 Real-time Chat** - Direct communication with Cerebro
- **📊 Live Monitoring** - Real-time status and performance metrics
- **🎨 Professional UI** - Stunning animations and responsive design
- **🖥️ Desktop App** - Tauri-based executable for offline use
- **🔧 Developer Tools** - Comprehensive API and debugging features

## 🚀 Ready to Explore?

**Start your journey into the Cerebro Galaxy:**

```bash
# Windows - Just double-click:
start_jarvis.bat

# Then open: http://localhost:5173
```

**Experience the future of AI interaction where your conversations dynamically shape a living galaxy of intelligent agents!** 🧠🌌✨
