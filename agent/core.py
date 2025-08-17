import agent.tools as tools

ACTION_TOOLS = {"file_update", "browser_automation", "automation_task"}

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
        if any(w in msg_lower for w in ["what", "how", "why", "explain", "summarize", "analyze", "reason", "context", "rag"]):
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