# Janus: Private, Real-time AI Research Assistant

Janus is a privacy-first AI chat application that runs entirely on your local machine. It lets you interact with a locally hosted Large Language Model (LLM) via a modern web UI, with optional real-time information retrieval from the web to enhance your answers. All processing is local; only anonymized web queries for context retrieval are sent externally.

---

## Features

- **Persistent Chat:** Modern UI with session-long history.
- **Model Selection:** Choose any locally available model (Llama 3, Mixtral, etc.) from the sidebar.
- **Real-time Web Search (RAG):** Toggle to augment answers with up-to-date web info.
- **Streaming Responses:** Watch the AI type answers live, token by token.
- **Source Citations:** See the sources used for web-augmented replies.

---

## Requirements

- **Python 3.10+**
- **Ollama** (must be installed and running locally)
- **pip** (for installing Python dependencies)

---

## Installation

1. **Clone the repository**

   ```
   git clone https://github.com/yourusername/janus_ai.git
   cd janus_ai
   ```

2. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

3. **Install and start Ollama**

   - [Ollama installation guide](https://ollama.com/download)
   - Start Ollama:
     ```
     ollama serve
     ```
   - Pull at least one model (e.g., Llama 3):
     ```
     ollama pull llama3
     ```

---

## Running Janus

1. **Start the app**

   ```
   streamlit run app.py
   ```

2. **Visit** [http://localhost:8501](http://localhost:8501) in your browser.

---

## Project Structure

```
janus_ai/
│
├── app.py              # Main Streamlit application logic
├── ollama_client.py    # Handles all communications with Ollama
├── rag_handler.py      # Web search and prompt augmentation logic
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Configuration Notes

- **No API keys required.** Everything runs locally.
- **Privacy:** Only anonymized search queries are sent out for context retrieval.
- **Extensible:** Modular codebase for easy future upgrades.

---

## Troubleshooting

- Ensure Ollama is running (`localhost:11434`).
- If models aren’t listed, make sure you’ve pulled them with `ollama pull <modelname>`.

---

## License

MIT

---

Enjoy a truly private, cutting-edge AI assistant!
