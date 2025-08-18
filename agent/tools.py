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
import requests

def preview_tool_action(step):
    return f"Will run {step['tool']} with args {step['args']}"

def run_tool(step, expert_model=None, draft_model=None, user=None):
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