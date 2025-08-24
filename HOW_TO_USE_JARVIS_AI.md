# 🎯 **How to Interact with Jarvis AI - Complete User Guide**

## 🚀 **Getting Started - Multiple Ways to Launch**

### **1. Quick Launch (Recommended)**
```batch
# Just run the launcher
start_launcher.bat
```

The launcher gives you these options:
- **🖥️ Desktop App (Basic)** - Simple tkinter interface
- **🎨 Desktop App (Modern)** - Sleek customtkinter UI
- **🌐 Web UI** - Full-featured Streamlit interface (recommended)
- **💻 CLI** - Command line interface
- **🧪 Test Workflow** - Run agentic workflow tests
- **📊 LangSmith Dashboard** - Open monitoring dashboard

### **2. Direct CLI Access**
```bash
# Using the CLI directly
python -m jarvis_ai.cli run
python -m jarvis_ai.cli config --show
python -m jarvis_ai.cli config --validate
```

### **3. Web Interface (Most Features)**
```bash
# Direct streamlit launch
jarvis run
```

## 🔐 **Authentication & User Management**

### **Initial Setup**
1. **First Run**: Creates default admin account
2. **Admin Login**: Use admin credentials to access full features
3. **User Registration**: Admins can enable/disable user registration

### **Login Process**
- **Standard Users**: Basic AI assistant features
- **Admin Users**: Full system management capabilities
- **Security Features**: 
  - Rate limiting (max 5 failed attempts)
  - Account lockout protection
  - Security event logging
  - Bcrypt password hashing

### **Admin Panel Access**
```
Login as admin → Sidebar → Admin Panel
```

**Admin Features:**
- 👥 User Management (activate/deactivate users)
- ⏳ Pending User Approvals
- 📊 Security Logs & Monitoring
- 🤖 Ollama Model Management
- ⚙️ System Settings
- 📈 Analytics Dashboard

## 🤖 **AI Model Management**

### **Ollama Integration**
The system uses Ollama for local AI models:

**Available Models:**
- `llama3.2` - General purpose
- `qwen2.5` - Code and reasoning
- `gemma2` - Google's lightweight model
- `codellama` - Specialized for coding

**Model Management (Admin Panel):**
1. **Check Connection** - Test Ollama endpoint
2. **Pull Models** - Download new models
3. **Health Check** - Test all models
4. **Remove Models** - Clean up unused models

**Model Endpoints:**
- Default: `http://localhost:11434`
- Configurable in admin panel

## 🔧 **Core Features & How to Use Them**

### **1. AI Chat Interface**
- **Basic Chat**: Ask questions, get AI responses
- **Context Awareness**: Maintains conversation history
- **Model Selection**: Choose from available Ollama models
- **Streaming Responses**: Real-time response generation

### **2. Lang Ecosystem Integration**
The system includes:
- **LangChain**: For AI model operations
- **LangGraph**: For workflow orchestration
- **LangSmith**: For monitoring and observability

**Accessing Lang Features:**
```python
# LangGraph workflows available in UI
# LangSmith monitoring at https://smith.langchain.com/
```

### **3. Plugin System**
**Built-in Plugins:**
- **Code Intelligence** - Code analysis and suggestions
- **Human-in-Loop** - Human approval workflows
- **Analytics** - Usage tracking and insights
- **File Management** - Upload and process files

**Accessing Plugins:**
- Sidebar → Plugin options
- Admin Panel → Plugin configuration

### **4. Security & Privacy**
**Privacy-First Features:**
- Local processing (no data sent to external APIs)
- Encrypted data storage
- User permission controls
- Audit logging

**Security Monitoring:**
- Failed login tracking
- IP address logging
- Event auditing
- Rate limiting

## 📊 **Analytics & Monitoring**

### **User Analytics**
- **Usage Patterns** - How you use the system
- **Model Performance** - Response times and accuracy
- **Feature Adoption** - Which features are most used

### **System Analytics (Admin)**
- **Resource Usage** - CPU, memory, disk usage
- **User Activity** - Login patterns, active users
- **Model Health** - Performance metrics
- **Security Events** - Threat detection

**Accessing Analytics:**
```
Sidebar → Analytics
Admin Panel → Analytics Tab
```

## 🛠️ **Customization & Workflows**

### **Custom Workflows**
The system supports custom workflow creation:

**Available Templates:**
- **Data Analysis Workflow** - For data processing tasks
- **Research Workflow** - For information gathering
- **API Integration Workflow** - For external service integration

**Creating Custom Workflows:**
1. **Use Templates** - Start with pre-built templates
2. **Define Steps** - Planning → Execution → Analysis → Synthesis
3. **Add Tools** - Integrate custom tools and APIs
4. **Test & Deploy** - Validate workflow before production use

### **Integration Options**
**Database Integration:**
- SQLite for persistent storage
- Analytics data tracking
- User preference storage

**API Integrations:**
- Weather APIs
- News APIs
- Slack integration
- Custom REST APIs

**Tool Development:**
- File processors
- Web scrapers
- Data analytics tools
- Notification systems

## 📁 **File & Data Management**

### **File Upload System**
- **Supported Formats**: Text, images, documents
- **Security Scanning**: Automatic file validation
- **Size Limits**: Configurable by admin
- **Storage**: Local file system with encryption

### **Data Processing**
- **RAG (Retrieval-Augmented Generation)** - Document Q&A
- **Code Analysis** - Programming assistance
- **Data Analytics** - Statistical analysis and visualization

## 🔄 **System Integration Workflows**

### **End-to-End Workflow Example:**

1. **User Login** → Authentication system validates credentials
2. **Model Selection** → Choose appropriate AI model for task
3. **Task Execution** → AI processes request using LangChain
4. **Workflow Orchestration** → LangGraph manages complex multi-step tasks
5. **Result Processing** → System analyzes and formats response
6. **Analytics Logging** → Usage data recorded for monitoring
7. **Security Audit** → All actions logged for security compliance

### **Integration Points:**
- **Frontend**: Streamlit web interface
- **Backend**: FastAPI for API endpoints
- **AI Engine**: Ollama + LangChain integration
- **Database**: SQLite for persistence
- **Monitoring**: LangSmith + custom analytics
- **Security**: bcrypt + session management

## 🚨 **Troubleshooting Common Issues**

### **Authentication Problems**
```bash
# Reset admin password
python scripts/create_admin_user.py

# Check user database
python list_users.py
```

### **Model Issues**
```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Pull a model manually
ollama pull llama3.2
```

### **Performance Issues**
```bash
# Check system resources
python system_monitor.py

# Validate deployment
bash scripts/validate_deployment.sh
```

### **Configuration Problems**
```bash
# Validate configuration
jarvis config --validate

# Reset to defaults
jarvis config --init
```

## 🔄 **Best Practices**

### **For Users:**
1. **Start Simple** - Use basic chat before advanced features
2. **Check Model Status** - Ensure Ollama models are healthy
3. **Save Important Conversations** - Use export features
4. **Monitor Usage** - Check analytics for insights

### **For Administrators:**
1. **Regular Health Checks** - Monitor system performance
2. **User Management** - Review pending registrations
3. **Security Monitoring** - Check security logs regularly
4. **Model Updates** - Keep AI models current
5. **Backup Configuration** - Save system settings

### **For Developers:**
1. **Use Templates** - Start with workflow templates
2. **Test Thoroughly** - Validate custom integrations
3. **Monitor Performance** - Use LangSmith tracking
4. **Follow Security** - Implement proper authentication

## 📈 **Advanced Features**

### **Multi-Agent Workflows**
- **Coordinator Agent** - Manages task distribution
- **Specialist Agents** - Handle specific domains
- **Human-in-Loop** - Manual approval steps
- **Error Handling** - Fallback mechanisms

### **Real-Time Processing**
- **Streaming Responses** - Live AI output
- **Event-Driven Architecture** - Reactive workflows
- **Background Tasks** - Long-running processes
- **Notification System** - Real-time alerts

### **Enterprise Features**
- **Role-Based Access Control** - Granular permissions
- **Audit Compliance** - Complete activity logging
- **Scalability** - Horizontal scaling support
- **API Management** - Rate limiting and quotas

## 🎯 **Getting Maximum Value**

### **Daily Usage Patterns:**
1. **Morning**: Check system health, review analytics
2. **Work Sessions**: Use AI assistant for tasks
3. **Periodic**: Review and approve workflows (if human-in-loop enabled)
4. **Evening**: Check security logs, system maintenance

### **Feature Exploration:**
1. **Week 1**: Basic chat and model selection
2. **Week 2**: Try custom workflows and integrations
3. **Week 3**: Explore admin features and analytics
4. **Week 4**: Develop custom tools and advanced workflows

### **Success Metrics:**
- **Productivity Gains** - Time saved on routine tasks
- **Quality Improvements** - Better decision-making with AI assistance
- **System Reliability** - Uptime and performance metrics
- **User Satisfaction** - Feedback and usage patterns

---

## 🆘 **Need Help?**

1. **Documentation**: Check `/docs` folder for detailed guides
2. **Logs**: Review `/logs/jarvis.log` for system events
3. **Community**: Check GitHub issues for common problems
4. **Support**: Use the built-in feedback system

**Remember**: Jarvis AI is designed to be privacy-first and locally controlled. All AI processing happens on your machine, ensuring your data stays secure and private.

---

*This guide covers the integrated system that combines all the completed features. For specific technical implementation details, refer to the individual documentation files in the `/docs` directory.*
