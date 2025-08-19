#!/bin/bash
# Automated launch script for Jarvis_AI
# Usage: bash launch.sh

set -e

# Start Ollama (if not running)
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 3
else
    echo "Ollama is already running."
fi



# Pull only qwen:6b model
echo "Pulling model: qwen:6b"
ollama pull "qwen:6b"

# Launch the Streamlit app
if [ -f "app.py" ]; then
    echo "Launching Streamlit app..."
    streamlit run app.py
else
    echo "app.py not found!"
    exit 1
fi
