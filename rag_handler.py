import requests

def rag_answer(prompt, files, model_name, chat_history, user, endpoint):
    # Use only provided files/context, send to RAG endpoint
    context = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                context.append(file.read()[:2000])  # limit size for API
        except Exception as e:
            context.append(f"[Could not read {f}: {e}]")
    payload = {
        "prompt": prompt,
        "context": context,
        "model_name": model_name,
        "chat_history": chat_history,
        "user": user
    }
    try:
        res = requests.post(endpoint, json=payload, timeout=30)
        if res.ok:
            return res.json().get("response", "RAG response not found.")
        else:
            return f"RAG API error: {res.status_code} {res.text}"
    except Exception as e:
        return f"RAG API request failed: {e}"