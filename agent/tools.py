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

def llm_api_call(prompt, expert_model, draft_model, chat_history, user, endpoint):
    # Build a more comprehensive prompt with context
    system_prompt = """You are Jarvis, an advanced AI assistant. Your areas of expertise include:
- Software development and coding assistance
- File analysis and document processing  
- Git repository management
- Code review and quality analysis
- IDE integration and development tools
- Note-taking and knowledge management
- Web automation and data extraction
- Image generation and processing

Always provide helpful, detailed responses. If asked about your capabilities, list the specific areas above."""
    
    # For debugging, let's simplify the prompt first
    simple_prompt = f"{system_prompt}\n\nUser question: {prompt}\n\nPlease provide a detailed response:"
    
    # If endpoint is Ollama, use /api/generate and correct payload
    if "11434" in str(endpoint):
        # Use expert_model as the model name
        model = expert_model or "llama3.2"
        payload = {
            "model": model,
            "prompt": simple_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        # Add speculative decoding if draft model is provided
        if draft_model and draft_model != model:
            payload["draft_model"] = draft_model
        
        try:
            res = requests.post(f"http://localhost:11434/api/generate", json=payload, timeout=120)
            
            if res.ok:
                data = res.json()
                
                # Ollama returns 'response' for some models, 'output' for others
                response = data.get("response", "").strip()
                if not response:
                    response = data.get("output", "").strip()
                if not response:
                    # Try other possible fields
                    response = data.get("text", "").strip()
                
                # Extract and separate DeepSeek reasoning tokens
                chain_of_thought = ""
                final_response = response
                
                if response:
                    import re
                    # Extract <think>...</think> blocks from DeepSeek models
                    think_matches = re.findall(r'<think>(.*?)</think>', response, flags=re.DOTALL)
                    
                    if think_matches:
                        chain_of_thought = "\n\n".join(think_matches).strip()
                        # Remove <think>...</think> blocks from final response
                        final_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
                        
                        # Return both CoT and final response as a structured object
                        result = {
                            "type": "cot_response",
                            "chain_of_thought": chain_of_thought,
                            "final_answer": final_response,
                            "raw_response": response
                        }
                        return result
                
                # No CoT found, return simple response
                if not final_response:
                    final_response = "I apologize, but I wasn't able to generate a proper response. Please try rephrasing your request."
                
                return final_response
            else:
                return f"LLM API error: {res.status_code} - Please check your Ollama connection and model availability."
        except requests.exceptions.Timeout:
            return f"The model '{model}' is taking too long to respond. Try using a smaller/faster model or check if Ollama is overloaded."
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"
    else:
        payload = {
            "prompt": simple_prompt,
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
                return f"LLM API error: {res.status_code} {res.text}"
        except Exception as e:
            return f"LLM API request failed: {e}"

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