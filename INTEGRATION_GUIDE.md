# 🤖 Jarvis AI - Running & Integration Guide

## 🚀 How to Run Jarvis AI

You now have multiple ways to interact with your Jarvis AI system:

### 1. 🖥️ **Desktop Applications** (Recommended for Desktop Use)

#### Basic Desktop App (Built-in UI)
```bash
python desktop_app.py
```
Or double-click: `start_desktop.bat`

**Features:**
- ✅ Dark theme interface
- ✅ Real-time workflow execution
- ✅ LangSmith integration
- ✅ Ollama status monitoring
- ✅ Multi-step agentic workflows

#### Modern Desktop App (Sleek UI)
```bash
pip install customtkinter
python modern_desktop_app.py
```

**Features:**
- ✅ Modern, sleek interface
- ✅ Better animations and styling
- ✅ All features of basic app

### 2. 🌐 **Web Interface** (Streamlit)

```bash
jarvis run
```
Or double-click: `start_web.bat`

**Access:** http://localhost:8501

### 3. 💻 **Command Line Interface**

```bash
python launcher.py
```
Or double-click: `start_launcher.bat`

### 4. 🧪 **Direct Workflow Testing**

```bash
python test_full_workflow.py
```

## 🔗 Integration Options

### API Integration
Create REST API endpoints:

```python
from flask import Flask, request, jsonify
from your_workflow import create_agentic_workflow

app = Flask(__name__)

@app.route('/api/workflow', methods=['POST'])
def run_workflow():
    query = request.json.get('query')
    result = create_agentic_workflow(query)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Database Integration
Connect to databases for persistent workflows:

```python
import sqlite3
from datetime import datetime

def save_workflow_result(query, result):
    conn = sqlite3.connect('jarvis_workflows.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY,
            query TEXT,
            result TEXT,
            timestamp DATETIME
        )
    ''')
    
    cursor.execute('''
        INSERT INTO workflows (query, result, timestamp)
        VALUES (?, ?, ?)
    ''', (query, result, datetime.now()))
    
    conn.commit()
    conn.close()
```

### Webhook Integration
Set up webhooks for external triggers:

```python
from flask import Flask, request
import threading

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    data = request.json
    
    # Process webhook data
    query = data.get('message', 'Default query')
    
    # Run workflow in background
    def run_async():
        result = create_agentic_workflow(query)
        # Send result back to webhook source
        
    threading.Thread(target=run_async).start()
    return {'status': 'processing'}
```

### Slack/Discord Bot Integration

```python
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.command(name='jarvis')
async def jarvis_command(ctx, *, query):
    await ctx.send("🤖 Processing your request...")
    
    result = create_agentic_workflow(query)
    
    # Split long messages
    if len(result) > 2000:
        chunks = [result[i:i+2000] for i in range(0, len(result), 2000)]
        for chunk in chunks:
            await ctx.send(chunk)
    else:
        await ctx.send(result)

bot.run('YOUR_BOT_TOKEN')
```

## 🛠️ Custom Tool Integration

### Add New Tools to Workflows

```python
def web_search_tool(query):
    """Custom web search tool."""
    # Implement web search logic
    return search_results

def database_query_tool(sql):
    """Custom database query tool."""
    # Implement database query logic
    return query_results

# Add to workflow
def enhanced_research_agent(plan):
    research = {}
    for step in plan:
        if "search" in step.lower():
            research[step] = web_search_tool(step)
        elif "database" in step.lower():
            research[step] = database_query_tool(step)
    return research
```

### File Processing Integration

```python
import pandas as pd
from pathlib import Path

def process_file_upload(file_path):
    """Process uploaded files."""
    file_path = Path(file_path)
    
    if file_path.suffix == '.csv':
        df = pd.read_csv(file_path)
        return f"Processed CSV with {len(df)} rows"
    elif file_path.suffix == '.txt':
        with open(file_path, 'r') as f:
            content = f.read()
        return f"Processed text file with {len(content)} characters"
    
    return "Unsupported file type"
```

## 📊 Monitoring & Analytics

### LangSmith Dashboard
- **URL:** https://smith.langchain.com/
- **Features:** 
  - ✅ Workflow tracing
  - ✅ Performance metrics
  - ✅ Error tracking
  - ✅ Cost analysis

### Custom Analytics

```python
import time
from datetime import datetime

class WorkflowAnalytics:
    def __init__(self):
        self.metrics = []
    
    def track_workflow(self, query, execution_time, success=True):
        self.metrics.append({
            'timestamp': datetime.now(),
            'query': query,
            'execution_time': execution_time,
            'success': success
        })
    
    def get_performance_report(self):
        total_workflows = len(self.metrics)
        avg_time = sum(m['execution_time'] for m in self.metrics) / total_workflows
        success_rate = sum(1 for m in self.metrics if m['success']) / total_workflows
        
        return {
            'total_workflows': total_workflows,
            'average_execution_time': avg_time,
            'success_rate': success_rate * 100
        }

# Usage
analytics = WorkflowAnalytics()

def timed_workflow(query):
    start_time = time.time()
    try:
        result = create_agentic_workflow(query)
        execution_time = time.time() - start_time
        analytics.track_workflow(query, execution_time, True)
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        analytics.track_workflow(query, execution_time, False)
        raise e
```

## 🔐 Security & Authentication

### API Key Management

```python
import os
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('JARVIS_API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/secure-workflow', methods=['POST'])
@require_api_key
def secure_workflow():
    # Protected endpoint
    pass
```

## 🚀 Deployment Options

### 1. Local Desktop Deployment
- ✅ Double-click `.bat` files
- ✅ Python virtual environment
- ✅ All features available

### 2. Web Server Deployment
```bash
# Using Jarvis
jarvis run --port 8501 --host 0.0.0.0

# Using Flask API
python flask_api.py
```

### 3. Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["jarvis", "run", "--host", "0.0.0.0"]
```

### 4. Cloud Deployment
- **Streamlit Cloud:** Direct GitHub integration
- **Heroku:** Web app deployment
- **AWS/Azure:** Full cloud infrastructure

## 📋 Quick Start Checklist

✅ **Environment Setup**
- Virtual environment created
- Dependencies installed
- Environment variables configured

✅ **Core Components**
- LangSmith connection verified
- Ollama models available
- Agentic workflows tested

✅ **UI Options Available**
- Desktop app (basic & modern)
- Web interface (Streamlit)
- CLI interface
- Direct Python scripts

✅ **Integration Ready**
- API endpoints can be added
- Database connections possible
- Webhook handlers available
- Custom tools can be integrated

## 🎯 Next Steps

1. **Choose Your Interface:** Desktop, Web, or CLI
2. **Customize Workflows:** Add domain-specific logic
3. **Integrate Tools:** Add databases, APIs, file processing
4. **Deploy:** Choose local, web server, or cloud deployment
5. **Monitor:** Use LangSmith for observability

Your Jarvis AI system is now production-ready! 🚀
