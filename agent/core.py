import agent.tools as tools

ACTION_TOOLS = {"file_update", "browser_automation", "automation_task", "git_command", "github_api", "ide_command"}

class JarvisAgent:
    def __init__(self, persona_prompt, tool_registry, approval_callback, expert_model=None, draft_model=None, user=None, llm_endpoint=None, rag_endpoint=None):
        self.persona_prompt = persona_prompt
        self.tools = tool_registry
        self.approval_callback = approval_callback
        self.expert_model = expert_model
        self.draft_model = draft_model
        self.user = user
        self.llm_endpoint = llm_endpoint
        self.rag_endpoint = rag_endpoint

    def parse_natural_language(self, user_msg, available_files, chat_history=None):
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
        
        # GitHub API commands
        elif any(phrase in msg_lower for phrase in ["create pr", "create pull request", "create issue", "list issues", "list prs"]):
            action = "repo_info"  # default
            if "create pr" in msg_lower or "create pull request" in msg_lower:
                action = "create_pr"
            elif "create issue" in msg_lower:
                action = "create_issue"
            elif "list issues" in msg_lower:
                action = "list_issues"
            elif "list prs" in msg_lower:
                action = "list_prs"
            
            plan.append({
                "tool": "github_api",
                "args": {
                    "action": action,
                    "token": None,  # Will use environment variables
                    "repository": None
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
            if available_files:
                plan.append({
                    "tool": "llm_rag",
                    "args": {
                        "prompt": user_msg,
                        "files": available_files,
                        "chat_history": chat_history or [],
                        "user": self.user,
                        "rag_endpoint": self.rag_endpoint
                    }
                })
            else:
                plan.append({
                    "tool": "llm_task",
                    "args": {
                        "prompt": user_msg,
                        "chat_history": chat_history or [],
                        "user": self.user,
                        "llm_endpoint": self.llm_endpoint
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
            import re
            match = re.search(r"(https?://[^\s]+)", user_msg)
            actions = []
            if match:
                actions.append({"type": "goto", "url": match.group(1)})
            plan.append({"tool": "browser_automation", "args": {"actions": actions}})
        elif "image" in msg_lower or "picture" in msg_lower or "generate" in msg_lower:
            plan.append({"tool": "image_generation", "args": {"prompt": user_msg}})
        else:
            plan.append({"tool": "llm_task", "args": {"prompt": user_msg, "chat_history": chat_history or [], "user": self.user, "llm_endpoint": self.llm_endpoint}})
        return plan

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