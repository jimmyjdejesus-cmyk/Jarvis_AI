import agent.features.file_ingest as file_ingest
import agent.features.browser_automation as browser_automation
import agent.features.image_generation as image_generation
import agent.features.rag_handler as rag_handler
import agent.features.code_review as code_review
import agent.features.code_search as code_search
import agent.features.repo_context as repo_context
from tools.code_intelligence import engine as code_intelligence
import requests
import os
import shlex
import subprocess
import re
from agent.integrations.jetbrains_integration import JetBrainsIntegration

ALLOWED_GIT_COMMANDS = {"status", "log", "branch"}


def run_git_command(repository_path: str, command: str) -> str:
    """Execute a restricted git command in the specified repository.

    Args:
        repository_path: Path to the git repository.
        command: Git command string (e.g., "status").

    Returns:
        Output from the git command.

    Raises:
        FileNotFoundError: If the repository path is missing or invalid.
        ValueError: If the command is not allowed or contains unsafe characters.
        RuntimeError: If the git command fails to execute.
    """
    if not repository_path:
        raise FileNotFoundError("Repository path is required")
    repo_git = os.path.join(repository_path, ".git")
    if not os.path.isdir(repository_path) or not os.path.isdir(repo_git):
        raise FileNotFoundError(f"Repository not found: {repository_path}")

    tokens = shlex.split(command)
    if not tokens or tokens[0] not in ALLOWED_GIT_COMMANDS:
        raise ValueError("Unsupported git command")

    token_re = re.compile(r"^[\w./-]+$")
    for token in tokens:
        if not token_re.match(token):
            raise ValueError("Invalid characters in command")

    try:
        result = subprocess.run(
            ["git", "-C", repository_path] + tokens,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip()
        raise RuntimeError(stderr or "Git command failed") from e


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
        return run_git_command(repository_path, command)
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
    elif step['tool'] == "code_completion":
        file_path = step['args'].get("file_path", "")
        cursor_line = step['args'].get("cursor_line", 1)
        cursor_column = step['args'].get("cursor_column", 0)
        model = step['args'].get("model", "llama3.2")
        return code_intelligence.get_code_completion(file_path, cursor_line, cursor_column, model, user or 'anonymous')
    elif step['tool'] == "code_completion_feedback":
        file_path = step['args'].get("file_path", "")
        cursor_line = step['args'].get("cursor_line", 1)
        cursor_column = step['args'].get("cursor_column", 0)
        suggestion = step['args'].get("suggestion", "")
        accepted = step['args'].get("accepted", False)
        return code_intelligence.record_completion_feedback(file_path, cursor_line, cursor_column, suggestion, accepted, user or 'anonymous')
    elif step['tool'] == "github_api":
        action = step['args'].get("action", "")
        # TODO: Implement proper github API integration
        return f"GitHub API action '{action}' requested but integration module not available yet"
    elif step['tool'] == "ide_command":
        command = step['args'].get("command", "")
        ide_type = step['args'].get("ide_type", "pycharm")
        ide = JetBrainsIntegration(ide_type)

        if command == "open_file":
            file_path = step['args'].get("file_path", "")
            line_number = step['args'].get("line_number")
            confirm = input(f"Open {file_path} in {ide_type}? [y/N]: ").strip().lower()
            if confirm == 'y':
                return ide.open_file(file_path, line_number)
            return {"cancelled": True}

        elif command == "run_lint":
            target = step['args'].get("target", "")
            confirm = input(f"Run lint on {target} in {ide_type}? [y/N]: ").strip().lower()
            if confirm == 'y':
                # Use 'inspect' command for linting via CLI
                return ide.run_ide_command("inspect", [target])
            return {"cancelled": True}

        else:
            return {"error": f"Unsupported IDE command: {command}"}
    elif step['tool'] == "note_command":
        command = step['args'].get("command", "")
        # TODO: Implement proper note integration
        return f"Note command '{command}' requested but note_integration module not available yet"
    elif step['tool'] == "repo_context":
        repository_path = step['args'].get("repository_path")
        return repo_context.get_repository_context(repository_path)
    else:
        return None

def initialize_plugin_system():
    """Initialize the plugin system and register all plugins."""
    try:
        from agent.adapters.plugin_registry import plugin_manager
        return plugin_manager.initialize()
    except Exception as e:
        print(f"Error initializing plugin system: {e}")
        return False

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

When answering complex questions, show your reasoning process using <think>...</think> tags before providing your final answer.

Always provide helpful, detailed responses. If asked about your capabilities, list the specific areas above."""

    # For debugging, let's simplify the prompt first
    simple_prompt = f"""{system_prompt}

User question: {prompt}

Please think through this step by step and provide a detailed response. Use <think>...</think> tags to show your reasoning process if this is a complex question."""

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

                # Extract and separate reasoning tokens from various models
                chain_of_thought = ""
                final_response = response

                if response:
                    import re

                    # Extract <think>...</think> blocks from DeepSeek models
                    think_matches = re.findall(r'<think>(.*?)</think>', response, flags=re.DOTALL)

                    # Extract <reasoning>...</reasoning> blocks from other models
                    if not think_matches:
                        think_matches = re.findall(r'<reasoning>(.*?)</reasoning>', response, flags=re.DOTALL)

                    # Extract **Thinking:** sections from models like Claude
                    if not think_matches:
                        think_matches = re.findall(r'\*\*Thinking:\*\*(.*?)(?=\*\*[A-Z]|$)', response, flags=re.DOTALL)

                    # Extract Chain of Thought: sections
                    if not think_matches:
                        think_matches = re.findall(r'Chain of Thought:(.*?)(?=Answer:|Final Answer:|$)', response, flags=re.DOTALL)

                    # Extract Let me think... patterns
                    if not think_matches:
                        think_matches = re.findall(r'Let me think[^.]*\.(.*?)(?=(?:So|Therefore|In conclusion|Final answer))', response, flags=re.DOTALL)

                    if think_matches:
                        chain_of_thought = "\n\n".join(think_matches).strip()
                        # Remove all reasoning blocks from final response
                        patterns_to_remove = [
                            r'<think>.*?</think>',
                            r'<reasoning>.*?</reasoning>',
                            r'\*\*Thinking:\*\*.*?(?=\*\*[A-Z]|$)',
                            r'Chain of Thought:.*?(?=Answer:|Final Answer:|$)',
                            r'Let me think[^.]*\..*?(?=(?:So|Therefore|In conclusion|Final answer))'
                        ]
                        for pattern in patterns_to_remove:
                            final_response = re.sub(pattern, '', final_response, flags=re.DOTALL).strip()
                        
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