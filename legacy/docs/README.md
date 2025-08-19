# Jarvis AI - Privacy-First Modular AI Development Assistant

About
-----

Jarvis AI is a local-first, modular development assistant that helps engineers automate repetitive tasks, analyze code, manage repositories, and integrate with IDEs and external services — while keeping all source code and data under your control.

Core goals:
- Local-first model hosting (Ollama) to avoid sending code upstream
- A pluginable architecture so teams can extend capabilities safely
- Git and IDE integration to speed up common developer workflows

Quick snapshot
--------------

Key capabilities: Git operations, semantic code search, automated code review, IDE open-in commands, RAG-enabled responses using local models, and integrations with GitHub, Notion, and OneNote.

Why use Jarvis AI?
- Keeps sensitive source code on-premise or on your machine
- Makes common developer tasks faster (search, refactor suggestions, PR prep)
- Extensible adapters let you add proprietary integrations securely

---

## 🚀 Enhanced Features

### **Development Workflow Integration**
- **Git Commands:** Execute git operations through natural language (`git status`, `git commit <msg>`, `git diff`)
- **IDE Integration:** Open files in JetBrains IDEs (`open in pycharm <path>`, `open in intellij <file>:line`)
- **Code Review:** Automated code quality analysis with style, security, and best practices checks
- **Code Search:** Semantic and lexical search across repositories with function/class/variable detection

### **Repository Intelligence**
- **Context Analysis:** Comprehensive repository structure, dependencies, and git history analysis
- **LLM/RAG Integration:** Surface repository context for enhanced AI responses
- **Documentation Discovery:** Automatic detection and indexing of project documentation

### **External Integrations**
- **GitHub API:** Repository management, issue/PR creation, branch operations
- **Notion Integration:** Save notes and create pages with OAuth support
- **OneNote Integration:** Microsoft Graph API integration for note management
- **JetBrains IDEs:** Full support for PyCharm, IntelliJ IDEA, WebStorm, PHPStorm, etc.

### **Core AI Capabilities**
- **Persistent Chat:** Modern UI with session-long history
- **Model Selection:** Choose any locally available model (Llama 3, Mixtral, etc.)
- **Real-time Web Search (RAG):** Toggle to augment answers with up-to-date web info
- **DuckDuckGo Fallback:** In the sidebar, enable "Use DuckDuckGo as fallback for web search" to allow the assistant to use DuckDuckGo when your main RAG endpoint returns no results or is unavailable. This ensures you always get a web answer if your local/external RAG can't help.

### How RAG Fallback Works
- If enabled, the assistant will first use your configured RAG endpoint (local vector DB, LangChain, or external API).
- If no results are found, or the endpoint is unavailable, it will automatically query DuckDuckGo and use those results for context.
- You can disable this fallback in the sidebar settings if you want only local/external results.

**Tip:** For best results, keep DuckDuckGo fallback enabled unless you need strict local-only answers.

---

## 🛠 Requirements

- **Python 3.10+**
- **Ollama** (must be installed and running locally for model hosting)
- **Git** (for repository operations)
- **JetBrains IDEs** (optional, for IDE integration)

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/jimmyjdejesus-cmyk/Jarvis_AI.git
   cd Jarvis_AI
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements_Version2.txt
   pip install GitPython psutil pytesseract python-docx pdfplumber PyPDF2 selenium playwright Pillow streamlit
   ```

3. **Install and start Ollama**

- [Ollama installation guide](https://ollama.com/download)
- Start Ollama locally:
   ```powershell
   ollama serve
   ```
- Pull at least one model (e.g., Llama 3):
   ```powershell
   ollama pull llama3
   ```

4. **Set up integrations (optional)**

   ```bash
   # GitHub integration
   export GITHUB_TOKEN="your_github_token"
   
   # Notion integration
   export NOTION_TOKEN="your_notion_integration_token"
   export NOTION_DATABASE_ID="your_database_id"
   
   # OneNote integration
   export ONENOTE_TOKEN="your_microsoft_graph_token"
   ```

---

## 🏃 Running Jarvis AI

1. **Start the application**

   ```bash
   streamlit run app.py
   ```

2. **Visit** [http://localhost:8501](http://localhost:8501) in your browser

3. **Try the enhanced commands:**
   - `git status` - Check repository status
   - `open in pycharm src/main.py:42` - Open file in PyCharm at specific line
   - `save to notion Today's progress notes` - Save text to Notion
   - `review code quality` - Analyze code for issues and suggestions
   - `search code for authenticate` - Find code patterns across repository
   - `show project structure` - Get comprehensive repository overview

---

## 📋 Command Examples

### Git Operations
```bash
git status                    # Check repository status
git commit "fix bug in auth"  # Commit changes with message
git diff                      # Show changes
git branch                    # List branches
```

### IDE Integration
```bash
open in pycharm app.py:25     # Open file at specific line
open in intellij README.md    # Open file in IntelliJ IDEA
open in webstorm src/app.js   # Open JavaScript file in WebStorm
```

### Note-taking
```bash
save to notion Meeting notes from today's standup
save to onenote Code review feedback for PR #123
create note in notion Project architecture thoughts
```

### Code Analysis
```bash
review code quality           # Analyze current files for quality issues
search code for JarvisAgent   # Find class/function references
find function parse_command   # Search for specific functions
analyze code complexity       # Get complexity metrics
```

### Repository Management
```bash
show project structure        # Get comprehensive repo overview
repo context                  # Generate LLM-friendly context
list recent commits          # Show git history
create issue for bug fix     # Create GitHub issue (requires token)
```

---

## 🏗 Project Structure

```
Jarvis_AI/
│
├── app.py                    # Main Streamlit application
├── agent/
│   ├── core.py              # Enhanced agent with new command parsing
│   ├── tools.py             # Expanded tool registry
│   ├── rag_handler.py       # RAG processing and file context
│   ├── code_review.py       # Code quality analysis
│   ├── code_search.py       # Semantic/lexical code search
│   ├── github_integration.py # GitHub API and git operations
│   ├── jetbrains_integration.py # IDE integration
│   ├── note_integration.py  # Notion/OneNote integration
│   ├── repo_context.py      # Repository intelligence
│   ├── file_ingest.py       # File processing capabilities
│   ├── browser_automation.py # Web automation
│   ├── image_generation.py  # AI image generation
│   ├── human_in_loop.py     # User approval workflows
│   └── security.py          # Authentication and encryption
├── ui/                      # Streamlit UI components
├── demo_enhanced_features.py # Feature demonstration script
└── README.md               # This file
```

---

## ⚙️ Configuration

### API Tokens
Set environment variables for external integrations:

```bash
# GitHub (for repository operations)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Notion (for note-taking)
export NOTION_TOKEN="secret_xxxxxxxxxxxxxxxxxxxx"
export NOTION_DATABASE_ID="xxxxxxxxxxxxxxxxxxxx"

# OneNote (Microsoft Graph)
export ONENOTE_TOKEN="xxxxxxxxxxxxxxxxxxxx"
```

### IDE Setup
Ensure JetBrains IDEs are installed and accessible in your PATH:
- PyCharm Community/Professional
- IntelliJ IDEA Community/Ultimate
- WebStorm, PHPStorm, CLion, GoLand, Rider

### Local Models
Configure Ollama with your preferred models:
```bash
ollama pull llama3          # General purpose
ollama pull codellama       # Code-specific model
ollama pull mixtral         # Advanced reasoning
```

---

## 🧪 Testing

Run the feature demonstration:
```bash
python demo_enhanced_features.py
```

This will test all new capabilities and show example usage.

---

## Troubleshooting

- Ensure Ollama is running (`localhost:11434`).
- If models aren’t listed, make sure you’ve pulled them with `ollama pull <modelname>`.

---

## License

MIT

---

**Enjoy your enhanced AI-powered development workflow!** 🚀

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch following our [branching strategy](./BRANCHING_STRATEGY.md):
   - `feature/[number]-[description]` for new features
   - `bugfix/[number]-[description]` for bug fixes
   - `refactor/[number]-[description]` for code refactoring
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/[number]-[description]`)
5. Open a Pull Request

For more details on our development workflow, please see the [branching strategy documentation](./BRANCHING_STRATEGY.md).

---

## 🙏 Acknowledgments

- **Ollama** for local LLM hosting
- **Streamlit** for the beautiful UI framework
- **JetBrains** for excellent IDE APIs
- **GitHub, Notion, Microsoft** for integration APIs
