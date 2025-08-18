import agent.file_ingest as file_ingest
import agent.browser_automation as browser_automation
import agent.image_generation as image_generation
import agent.rag_handler as rag_handler
import agent.code_review as code_review
import agent.code_search as code_search
import agent.github_integration as github_integration
import agent.jetbrains_integration as jetbrains_integration
import agent.note_integration as note_integration
import agent.repo_context as repo_context
import agent.test_generator as test_generator
import agent.doc_generator as doc_generator
import agent.dependency_manager as dependency_manager
import agent.persona_manager as persona_manager
import requests

# New plugin system imports
try:
    from agent.plugin_registry import plugin_manager
    from agent.workflow_system import workflow_parser, workflow_executor
    from agent.plugin_adapters import (
        GitPlugin, IDEPlugin, CodeReviewPlugin, CodeSearchPlugin, BrowserAutomationPlugin
    )
    PLUGIN_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Plugin system not available: {e}")
    PLUGIN_SYSTEM_AVAILABLE = False

def preview_tool_action(step):
    """Preview what a tool action will do."""
    # Try new plugin system first
    if PLUGIN_SYSTEM_AVAILABLE:
        try:
            from agent.plugin_base import PluginAction
            action = PluginAction(
                name=step['tool'],
                description=f"Execute {step['tool']}",
                args=step['args']
            )
            preview = plugin_manager.preview_action(action)
            if preview != f"Action: {action.name} with args: {action.args}":
                return preview
        except Exception:
            pass
    
    # Fallback to legacy preview
    return f"Will run {step['tool']} with args {step['args']}"


def initialize_plugin_system():
    """Initialize the plugin system with existing tools."""
    if not PLUGIN_SYSTEM_AVAILABLE:
        return False
    
    try:
        # Register plugin adapters for existing tools
        plugin_manager.registry.register_plugin(GitPlugin())
        plugin_manager.registry.register_plugin(IDEPlugin()) 
        plugin_manager.registry.register_plugin(CodeReviewPlugin())
        plugin_manager.registry.register_plugin(CodeSearchPlugin())
        plugin_manager.registry.register_plugin(BrowserAutomationPlugin())
        
        print(f"Registered {len(plugin_manager.registry.list_plugins())} plugins")
        
        # Discover additional plugins (this would find any custom plugins)
        discovered = plugin_manager.initialize()
        print(f"Discovered {discovered} additional plugins")
        
        return True
    except Exception as e:
        print(f"Failed to initialize plugin system: {e}")
        import traceback
        traceback.print_exc()
        return False


def parse_workflow_command(command: str, context: dict = None):
    """Parse a command that might be a workflow."""
    if not PLUGIN_SYSTEM_AVAILABLE:
        return None
    
    try:
        workflow = workflow_parser.parse_workflow(command, context)
        return workflow
    except Exception as e:
        print(f"Workflow parsing failed: {e}")
        return None


def execute_workflow(workflow, approval_callback=None):
    """Execute a workflow with optional approval."""
    if not PLUGIN_SYSTEM_AVAILABLE:
        return None
    
    try:
        if approval_callback:
            workflow_executor.approval_callback = approval_callback
        
        result = workflow_executor.execute_workflow(workflow)
        return result
    except Exception as e:
        print(f"Workflow execution failed: {e}")
        return None

def run_tool(step, expert_model=None, draft_model=None, user=None):
    """Run a tool action, trying plugin system first, then falling back to legacy."""
    
    # Try new plugin system first
    if PLUGIN_SYSTEM_AVAILABLE:
        try:
            from agent.plugin_base import PluginAction
            action = PluginAction(
                name=step['tool'],
                description=f"Execute {step['tool']}",
                args=step['args']
            )
            
            result = plugin_manager.execute_action(action)
            if result.success:
                return result.output
            elif result.error != "No plugin found to execute action":
                return f"Plugin error: {result.error}"
        except Exception as e:
            print(f"Plugin execution failed: {e}")
    
    # Fallback to legacy tool execution
    if step['tool'] == "file_ingest":
        return [file_ingest.ingest_file(f) for f in step['args'].get("files", [])]
    elif step['tool'] == "file_list":
        return [f"File: {f}" for f in step['args'].get("files", [])]
    elif step['tool'] == "browser_automation":
        return browser_automation.automate_browser(step['args'].get("actions", []))
    elif step['tool'] == "image_generation":
        return image_generation.generate_image(step['args'].get("prompt", ""))
    elif step['tool'] == "llm_task":
        prompt = step['args'].get("prompt", "")
        chat_history = step['args'].get("chat_history", [])
        endpoint = step['args'].get("llm_endpoint")
        return llm_api_call(prompt, expert_model, draft_model, chat_history, user, endpoint)
    elif step['tool'] == "llm_rag":
        prompt = step['args'].get("prompt", "")
        files = step['args'].get("files", [])
        chat_history = step['args'].get("chat_history", [])
        endpoint = step['args'].get("rag_endpoint")
        mode = step['args'].get("mode", "file")
        return rag_handler.rag_answer(prompt, files, expert_model, chat_history, user, endpoint, mode)
    elif step['tool'] == "git_command":
        command = step['args'].get("command", "")
        repository_path = step['args'].get("repository_path")
        return github_integration.execute_git_command(command, repository_path)
    elif step['tool'] == "code_review":
        file_path = step['args'].get("file_path", "")
        check_types = step['args'].get("check_types")
        return code_review.review_file(file_path, check_types)
    elif step['tool'] == "code_search":
        query = step['args'].get("query", "")
        search_type = step['args'].get("search_type", "all")
        repository_path = step['args'].get("repository_path")
        case_sensitive = step['args'].get("case_sensitive", False)
        regex = step['args'].get("regex", False)
        return code_search.search_code(query, repository_path, search_type, case_sensitive, regex)
    elif step['tool'] == "github_api":
        action = step['args'].get("action", "")
        return github_integration.github_integration_handler(action, **step['args'])
    elif step['tool'] == "ide_command":
        command = step['args'].get("command", "")
        return jetbrains_integration.execute_ide_command(command)
    elif step['tool'] == "note_command":
        command = step['args'].get("command", "")
        notion_token = step['args'].get("notion_token")
        notion_db_id = step['args'].get("notion_db_id")
        onenote_token = step['args'].get("onenote_token")
        onenote_section_id = step['args'].get("onenote_section_id")
        return note_integration.execute_note_command(command, notion_token, notion_db_id, onenote_token, onenote_section_id)
    elif step['tool'] == "repo_context":
        repository_path = step['args'].get("repository_path")
        return repo_context.get_repository_context(repository_path)
    elif step['tool'] == "test_generator":
        action = step['args'].get("action", "generate")
        return test_generator.test_generator_handler(action, **step['args'])
    elif step['tool'] == "doc_generator":
        action = step['args'].get("action", "generate")
        return doc_generator.documentation_handler(action, **step['args'])
    elif step['tool'] == "dependency_manager":
        action = step['args'].get("action", "analyze")
        return dependency_manager.dependency_handler(action, **step['args'])
    elif step['tool'] == "persona_manager":
        action = step['args'].get("action", "list")
        return persona_manager.persona_handler(action, **step['args'])
    else:
        return None

def llm_api_call(prompt, expert_model, draft_model, chat_history, user, endpoint, session_id=None):
    import time
    import sys
    import os
    
    # Add parent directory to path to import analytics_tracker
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import analytics_tracker
    
    start_time = time.time()
    success = True
    error_message = None
    
    try:
        # If endpoint is Ollama, use /api/generate and correct payload
        if "11434" in endpoint:
            # Use expert_model as the model name
            model = expert_model or "llama2"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            try:
                res = requests.post(f"http://localhost:11434/api/generate", json=payload, timeout=60)
                if res.ok:
                    data = res.json()
                    # Ollama returns 'response' for some models, 'output' for others
                    response = data.get("response")
                    if response is None:
                        response = data.get("output")
                    if response is None:
                        # Show the full JSON if no recognized field
                        response = str(data)
                    return response
                else:
                    success = False
                    error_message = f"LLM API error: {res.status_code} {res.text}"
                    return error_message
            except Exception as e:
                success = False
                error_message = f"LLM API request failed: {e}"
                return error_message
        else:
            payload = {
                "prompt": prompt,
                "expert_model": expert_model,
                "draft_model": draft_model,
                "chat_history": chat_history,
                "user": user
            }
            try:
                res = requests.post(endpoint, json=payload, timeout=20)
                if res.ok:
                    return res.json().get("response", "LLM response not found.")
                else:
                    success = False
                    error_message = f"LLM API error: {res.status_code} {res.text}"
                    return error_message
            except Exception as e:
                success = False
                error_message = f"LLM API request failed: {e}"
                return error_message
    finally:
        # Log the API call with analytics
        latency_ms = int((time.time() - start_time) * 1000)
        
        try:
            analytics_tracker.log_chat_interaction(
                username=user or 'anonymous',
                session_id=session_id,
                user_message=prompt,
                ai_response="",  # We don't have the response here if it failed
                model_name=expert_model,
                latency_ms=latency_ms
            )
        except Exception as e:
            # Don't let analytics errors break the main function
            print(f"Analytics logging error: {e}")

def llm_summarize_source(source_text, endpoint):
    payload = {
        "prompt": f"Summarize this source for RAG usability:\n{source_text}",
    }
    try:
        res = requests.post(endpoint, json=payload, timeout=20)
        if res.ok:
            return res.json().get("response", "Summary not found.")
        else:
            return f"LLM API error: {res.status_code} {res.text}"
    except Exception as e:
        return f"LLM API request failed: {e}"