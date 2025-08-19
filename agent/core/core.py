import agent.tools as tools

ACTION_TOOLS = {"file_update", "browser_automation", "automation_task", "git_command", "github_api", "ide_command"}

# V2 LangGraph integration
try:
    from agent.core.langgraph_agent import get_agent as get_langgraph_agent, LANGGRAPH_AVAILABLE
    from agent.core.langchain_tools import get_available_tools
except ImportError:
    LANGGRAPH_AVAILABLE = False
    
    def get_langgraph_agent(**kwargs):
        return None
    
    def get_available_tools():
        return []


class JarvisAgent:
    def __init__(self, persona_prompt, tool_registry, approval_callback, expert_model=None, draft_model=None, user=None, llm_endpoint=None, rag_endpoint=None, duckduckgo_fallback=True, use_langgraph=True):
        self.persona_prompt = persona_prompt
        self.tools = tool_registry
        self.approval_callback = approval_callback
        self.expert_model = expert_model
        self.draft_model = draft_model
        self.user = user
        self.llm_endpoint = llm_endpoint
        self.rag_endpoint = rag_endpoint
        self.duckduckgo_fallback = duckduckgo_fallback
        self.use_langgraph = use_langgraph and LANGGRAPH_AVAILABLE
        
        # Initialize V2 LangGraph agent if available
        self.langgraph_agent = None
        if self.use_langgraph:
            try:
                langchain_tools = get_available_tools()
                self.langgraph_agent = get_langgraph_agent(
                    expert_model=expert_model,
                    tools=langchain_tools
                )
            except Exception as e:
                print(f"Could not initialize LangGraph agent: {e}")
                self.use_langgraph = False
        
        # Initialize plugin system
        try:
            from agent.tools import initialize_plugin_system
            self.plugin_system_enabled = initialize_plugin_system()
        except Exception as e:
            print(f"Could not initialize plugin system: {e}")
            self.plugin_system_enabled = False

    def parse_natural_language(self, user_msg, available_files, chat_history=None):
        """Parse natural language into executable plans, supporting workflows and LangGraph V2."""
        
        # V2: Try LangGraph agent first if available
        if self.use_langgraph and self.langgraph_agent:
            try:
                # Use LangGraph agent for more sophisticated planning
                result = self.langgraph_agent.invoke(user_msg)
                
                # Convert LangGraph result to V1-compatible plan format
                if isinstance(result, dict) and not result.get("error"):
                    plan = self._langgraph_result_to_plan(result, available_files)
                    if plan:
                        return plan
                else:
                    print(f"LangGraph error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"LangGraph agent error: {e}")
                # Fall back to V1 planning
        
        # First, try to parse as a workflow if plugin system is enabled
        if self.plugin_system_enabled:
            try:
                from agent.tools import parse_workflow_command
                
                context = {
                    "files": available_files,
                    "chat_history": chat_history,
                    "user": self.user
                }
                
                workflow = parse_workflow_command(user_msg, context)
                if workflow:
                    # Convert workflow to plan format for compatibility
                    plan = []
                    for step in workflow.steps:
                        plan.append({
                            "tool": step.action.name,
                            "args": step.action.args,
                            "description": step.action.description,
                            "requires_approval": step.action.requires_approval,
                            "workflow_step": True
                        })
                    return plan
            except Exception as e:
                print(f"Workflow parsing error: {e}")
        
        # Fallback to legacy parsing
        plan = []
        msg_lower = user_msg.lower()
        
        # Git commands
        if any(cmd in msg_lower for cmd in ["git status", "git commit", "git diff", "git push", "git pull", "git checkout", "git branch"]):
            plan.append({
                "tool": "git_command",
                "args": {
                    "command": user_msg,
                    "repository_path": None  # Will use current directory
                }
            })
        
        # IDE commands (PyCharm, IntelliJ, etc.)
        elif any(phrase in msg_lower for phrase in ["open in pycharm", "open in intellij", "open in idea", "open in webstorm", "open in phpstorm"]):
            plan.append({
                "tool": "ide_command",
                "args": {
                    "command": user_msg
                }
            })
        
        # Note-taking commands (Notion, OneNote)
        elif any(phrase in msg_lower for phrase in ["save to notion", "save to onenote", "create note", "search notes"]):
            plan.append({
                "tool": "note_command",
                "args": {
                    "command": user_msg,
                    "notion_token": None,  # Will use environment variables
                    "notion_db_id": None,
                    "onenote_token": None,
                    "onenote_section_id": None
                }
            })
        
        # Code review commands
        elif any(phrase in msg_lower for phrase in ["review code", "code review", "analyze code", "check code quality"]):
            # Extract file path if mentioned
            import re
            file_match = re.search(r'([^\s]+\.(py|js|ts|java|cpp|c|h|hpp|go|rs))', user_msg)
            if file_match:
                file_path = file_match.group(1)
            else:
                file_path = available_files[0] if available_files else ""
            
            plan.append({
                "tool": "code_review",
                "args": {
                    "file_path": file_path,
                    "check_types": ["style", "security", "complexity", "best_practices"]
                }
            })
        
        # Code search commands
        elif any(phrase in msg_lower for phrase in ["search code", "find function", "find class", "search for"]):
            # Extract search query
            search_phrases = ["search code", "find function", "find class", "search for"]
            query = user_msg
            for phrase in search_phrases:
                if phrase in msg_lower:
                    query = user_msg[user_msg.lower().find(phrase) + len(phrase):].strip()
                    break
            
            search_type = "all"
            if "function" in msg_lower:
                search_type = "function"
            elif "class" in msg_lower:
                search_type = "class"
            elif "variable" in msg_lower:
                search_type = "variable"
            
            plan.append({
                "tool": "code_search",
                "args": {
                    "query": query,
                    "search_type": search_type,
                    "repository_path": None,
                    "case_sensitive": False,
                    "regex": False
                }
            })
        
        # GitHub API commands (Enhanced with CI/CD)
        elif any(phrase in msg_lower for phrase in ["create pr", "create pull request", "create issue", "list issues", "list prs", 
                                                   "setup ci", "setup cicd", "list workflows", "trigger workflow", 
                                                   "deployment status", "security alerts", "triage issues"]):
            action = "repo_info"  # default
            if "create pr" in msg_lower or "create pull request" in msg_lower:
                action = "create_pr"
            elif "create issue" in msg_lower:
                action = "create_issue"
            elif "list issues" in msg_lower:
                action = "list_issues"
            elif "list prs" in msg_lower:
                action = "list_prs"
            elif "setup ci" in msg_lower or "setup cicd" in msg_lower:
                action = "setup_cicd"
            elif "list workflows" in msg_lower:
                action = "list_workflows"
            elif "trigger workflow" in msg_lower:
                action = "trigger_workflow"
            elif "deployment status" in msg_lower:
                action = "deployment_status"
            elif "security alerts" in msg_lower:
                action = "security_alerts"
            elif "triage issues" in msg_lower:
                action = "triage_issues"
            
            plan.append({
                "tool": "github_api",
                "args": {
                    "action": action,
                    "token": None,  # Will use environment variables
                    "repository": None
                }
            })
        
        # Test generation commands
        elif any(phrase in msg_lower for phrase in ["generate tests", "create tests", "test coverage", "analyze tests"]):
            action = "generate"
            if "coverage" in msg_lower:
                action = "coverage"
            elif "analyze" in msg_lower:
                action = "improve"
            
            # Extract file path if mentioned
            import re
            file_match = re.search(r'([^\\s]+\\.(py|js|ts|java|cpp|c|h|hpp|go|rs))', user_msg)
            file_path = file_match.group(1) if file_match else None
            
            plan.append({
                "tool": "test_generator",
                "args": {
                    "action": action,
                    "file_path": file_path,
                    "test_type": "unit",
                    "framework": None
                }
            })
        
        # Documentation generation commands
        elif any(phrase in msg_lower for phrase in ["generate docs", "create documentation", "document code", "api docs"]):
            action = "generate"
            if "api" in msg_lower:
                action = "api_docs"
            
            # Extract target path if mentioned
            import re
            path_match = re.search(r'([^\\s]+\\.(py|js|ts|java|cpp|c|h|hpp|go|rs|md))', user_msg)
            target_path = path_match.group(1) if path_match else "."
            
            plan.append({
                "tool": "doc_generator",
                "args": {
                    "action": action,
                    "target_path": target_path,
                    "doc_format": "markdown",
                    "include_private": False
                }
            })
        
        # Dependency management commands
        elif any(phrase in msg_lower for phrase in ["analyze dependencies", "check dependencies", "update dependencies", 
                                                   "dependency report", "security vulnerabilities", "outdated packages"]):
            action = "analyze"
            if "update" in msg_lower:
                action = "update"
            elif "report" in msg_lower:
                action = "report"
            
            plan.append({
                "tool": "dependency_manager",
                "args": {
                    "action": action,
                    "project_type": None,  # Auto-detect
                    "dry_run": True
                }
            })
        
        # Persona management commands
        elif any(phrase in msg_lower for phrase in ["list personas", "use persona", "switch persona", "recommend persona", 
                                                   "create persona", "persona help"]):
            action = "list"
            if "recommend" in msg_lower:
                action = "recommend"
            elif "create" in msg_lower:
                action = "create"
            elif "use" in msg_lower or "switch" in msg_lower:
                action = "get"
            
            plan.append({
                "tool": "persona_manager",
                "args": {
                    "action": action,
                    "task_type": None,
                    "persona_name": None
                }
            })
        
        # Repository context commands
        elif any(phrase in msg_lower for phrase in ["repo context", "repository context", "project overview", "show project structure"]):
            plan.append({
                "tool": "repo_context",
                "args": {
                    "repository_path": None
                }
            })
        
        # Existing logic for other commands
        elif any(w in msg_lower for w in ["what", "how", "why", "explain", "summarize", "analyze", "reason", "context", "rag"]):
            # Let user choose between file context or DuckDuckGo search
            mode = "file" if available_files else "search"
            plan.append({
                "tool": "llm_rag",
                "args": {
                    "prompt": user_msg,
                    "files": available_files,
                    "chat_history": chat_history or [],
                    "user": self.user,
                    "rag_endpoint": self.rag_endpoint,
                    "mode": mode,
                    "duckduckgo_fallback": self.duckduckgo_fallback
                }
            })
        elif any(w in msg_lower for w in ["show files", "list files", "what files", "display files"]):
            plan.append({"tool": "file_list", "args": {"files": available_files}})
        elif any(w in msg_lower for w in ["open file", "ingest file", "read file", "extract file"]):
            import re
            file_match = re.findall(r"([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)", user_msg)
            files_to_ingest = []
            for f in file_match:
                for available in available_files:
                    if f in available:
                        files_to_ingest.append(available)
            if not files_to_ingest:
                files_to_ingest = available_files
            if files_to_ingest:
                plan.append({"tool": "file_ingest", "args": {"files": files_to_ingest}})
        elif "browse" in msg_lower or "go to" in msg_lower or "scrape" in msg_lower or "update file" in msg_lower or "automate" in msg_lower:
            # Pass the natural language command for browser automation
            plan.append({"tool": "browser_automation", "args": {"actions": user_msg}})
        elif "image" in msg_lower or "picture" in msg_lower or "generate" in msg_lower:
            plan.append({"tool": "image_generation", "args": {"prompt": user_msg}})
        else:
            plan.append({"tool": "llm_task", "args": {"prompt": user_msg, "chat_history": chat_history or [], "user": self.user, "llm_endpoint": self.llm_endpoint}})
        return plan

    def _langgraph_result_to_plan(self, result, available_files):
        """
        Convert LangGraph workflow result to V1-compatible plan format.
        
        Args:
            result: LangGraph workflow execution result
            available_files: List of available files
            
        Returns:
            List of plan steps in V1 format
        """
        plan = []
        
        try:
            # Extract the plan from LangGraph result
            langgraph_plan = result.get("plan", {})
            
            if not langgraph_plan:
                # If no explicit plan, create one based on the task
                task = langgraph_plan.get("task", "")
                if "code" in task.lower():
                    plan.append({
                        "tool": "llm_task",
                        "args": {
                            "prompt": f"Generate code for: {task}",
                            "chat_history": [],
                            "user": self.user,
                            "llm_endpoint": self.llm_endpoint
                        }
                    })
                elif "file" in task.lower() and available_files:
                    plan.append({
                        "tool": "file_ingest",
                        "args": {"files": available_files}
                    })
                elif "git" in task.lower():
                    plan.append({
                        "tool": "git_command",
                        "args": {"command": task}
                    })
                else:
                    # Default to LLM task
                    plan.append({
                        "tool": "llm_task",
                        "args": {
                            "prompt": task,
                            "chat_history": [],
                            "user": self.user,
                            "llm_endpoint": self.llm_endpoint
                        }
                    })
            else:
                # Convert LangGraph plan steps to V1 format
                steps = langgraph_plan.get("steps", [])
                for step in steps:
                    if "code" in step.lower():
                        plan.append({
                            "tool": "llm_task",
                            "args": {
                                "prompt": f"Code generation: {step}",
                                "chat_history": [],
                                "user": self.user,
                                "llm_endpoint": self.llm_endpoint
                            }
                        })
                    elif "test" in step.lower():
                        plan.append({
                            "tool": "llm_task",
                            "args": {
                                "prompt": f"Test generation: {step}",
                                "chat_history": [],
                                "user": self.user,
                                "llm_endpoint": self.llm_endpoint
                            }
                        })
                    elif "file" in step.lower():
                        plan.append({
                            "tool": "file_ingest",
                            "args": {"files": available_files}
                        })
                    else:
                        plan.append({
                            "tool": "llm_task",
                            "args": {
                                "prompt": step,
                                "chat_history": [],
                                "user": self.user,
                                "llm_endpoint": self.llm_endpoint
                            }
                        })
            
            return plan
            
        except Exception as e:
            print(f"Error converting LangGraph result to plan: {e}")
            return None

    def execute_plan(self, plan):
        results = []
        for step in plan:
            if step['tool'] in ACTION_TOOLS:
                preview = self.tools.preview_tool_action(step)
                if not self.approval_callback(preview):
                    results.append({"step": step, "result": "Denied by user"})
                    continue
            result = self.tools.run_tool(
                step,
                expert_model=self.expert_model,
                draft_model=self.draft_model,
                user=self.user
            )
            results.append({"step": step, "result": result})
        return results