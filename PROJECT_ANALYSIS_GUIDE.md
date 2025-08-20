# 🚀 Jarvis AI - Project Analysis & IDE Integration Guide

## 📁 **How to Analyze Your Projects**

### **Method 1: Web Interface Project Selection**

1. **Open Jarvis AI Coding Assistant**: http://localhost:8504
2. **Login**: admin / admin123  
3. **In the sidebar**, find the "📁 Workspace" section
4. **Change Workspace**:
   - Click "Change Workspace" 
   - Enter your project path (e.g., `C:\Users\jimmy\MyProject`)
   - Click "Set Workspace"
5. **Click "Analyze Codebase"** to get full project analysis

### **Method 2: Command Line Integration**

Use the CLI tool for quick analysis:

```bash
# Analyze a specific file
python vscode_integration.py analyze-file --file "C:\path\to\your\file.py"

# Review code in a file
python vscode_integration.py review-code --file "C:\path\to\your\file.py" --language python

# Generate tests for a file
python vscode_integration.py generate-tests --file "C:\path\to\your\file.py"

# Analyze entire workspace
python vscode_integration.py analyze-workspace --workspace "C:\path\to\your\project"

# Explain code snippet
python vscode_integration.py explain-code --code "def hello(): print('world')" --language python

# Debug an error
python vscode_integration.py debug-error --error "IndexError: list index out of range" --language python
```

## 🔧 **IDE Integration Options**

### **Option 1: VS Code Integration (Recommended)**

**Step 1: Install the Extension Framework**
```bash
# Install VS Code extension dependencies
cd vscode_extension
npm install
npm run compile
```

**Step 2: Configure VS Code Settings**
Add to your VS Code `settings.json`:
```json
{
  "jarvis.pythonPath": "python",
  "jarvis.scriptPath": "C:\\Users\\jimmy\\Documents\\GitHub\\Jarvis_AI\\vscode_integration.py",
  "jarvis.autoAnalyze": false
}
```

**Step 3: Available Commands**
- `Ctrl+Shift+A`: Analyze current file
- `Ctrl+Shift+R`: Review code
- `Ctrl+Shift+E`: Explain selected code
- Right-click context menu options

### **Option 2: Any IDE via Command Palette**

Create keyboard shortcuts in your IDE to run:
```bash
python "C:\Users\jimmy\Documents\GitHub\Jarvis_AI\vscode_integration.py" analyze-file --file "%CURRENT_FILE%"
```

### **Option 3: Terminal/Command Line Workflow**

```bash
# Navigate to your project
cd "C:\your\project\path"

# Set the workspace in Jarvis
python -c "
import sys
sys.path.append('C:\\Users\\jimmy\\Documents\\GitHub\\Jarvis_AI')
import jarvis
base_agent = jarvis.get_jarvis_agent()
coding_agent = jarvis.get_coding_agent(base_agent, '.')
analysis = coding_agent.analyze_codebase()
print('Languages:', list(analysis['languages'].keys()))
print('Project type:', coding_agent._infer_project_type(analysis))
"
```

## 🎯 **Specific Use Cases**

### **Analyzing React/Node.js Projects**
```bash
# Set workspace to React project
python vscode_integration.py analyze-workspace --workspace "C:\path\to\react-app"

# Review a React component
python vscode_integration.py review-code --file "src\components\MyComponent.jsx" --language javascript
```

### **Analyzing Python Projects**
```bash
# Analyze Python package
python vscode_integration.py analyze-workspace --workspace "C:\path\to\python-project"

# Generate tests for Python module
python vscode_integration.py generate-tests --file "src\mymodule.py" --language python
```

### **Debugging Help**
```bash
# Get help with specific error
python vscode_integration.py debug-error --error "TypeError: 'NoneType' object is not subscriptable" --code "result = data[key]" --language python
```

## 🌐 **Web Interface Features**

### **Real-time Project Analysis**
1. Set your workspace path in the sidebar
2. Click "Analyze Codebase" 
3. View detected languages, dependencies, structure
4. Get project-specific coding advice

### **Mode-Specific Analysis**
- **🔍 Code Review Mode**: Paste files for review
- **🐛 Debug Mode**: Get help with errors
- **⚡ Generator Mode**: Create new code based on project context
- **🏗️ Architecture Mode**: Get advice specific to your project structure

## 🚀 **Quick Start Examples**

### **Example 1: Analyze This Jarvis Project**
```bash
# Analyze the Jarvis AI codebase itself
python vscode_integration.py analyze-workspace --workspace "C:\Users\jimmy\Documents\GitHub\Jarvis_AI"
```

### **Example 2: Review a Specific File**
```bash
# Review the coding agent file
python vscode_integration.py review-code --file "jarvis\agents\coding_agent.py" --language python
```

### **Example 3: Get Architecture Advice**
Open the web interface, select "🏗️ Architecture Advisor" mode, and ask:
> "How should I structure my Flask API project with database integration?"

## 📋 **Supported Languages & Frameworks**

**Languages**: Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, Ruby, PHP

**Frameworks Detected**: 
- Python: Django, Flask, FastAPI
- JavaScript: React, Node.js, Express
- Java: Spring Boot, Maven
- And more...

## 🔄 **Integration Workflow**

1. **Set Workspace**: Point Jarvis to your project directory
2. **Analyze Structure**: Get overview of languages, dependencies, patterns
3. **Use Specialized Modes**: Choose the right mode for your task
4. **Get Context-Aware Help**: Jarvis understands your project structure
5. **Apply Suggestions**: Use the generated code, tests, or advice

Your Jarvis AI now understands your entire codebase and provides context-aware assistance! 🎉
