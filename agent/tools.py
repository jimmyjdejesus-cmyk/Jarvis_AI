import agent.file_ingest as file_ingest
import agent.browser_automation as browser_automation
import agent.image_generation as image_generation
import agent.rag_handler as rag_handler
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
        return rag_handler.rag_answer(prompt, files, expert_model, chat_history, user, endpoint)
    else:
        return None

def llm_api_call(prompt, expert_model, draft_model, chat_history, user, endpoint):
    # Real API call
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