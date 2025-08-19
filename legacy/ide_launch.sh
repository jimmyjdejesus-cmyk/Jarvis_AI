#!/bin/bash
# IDE launch script for Jarvis_AI
# Usage: bash ide_launch.sh

set -e

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama (if not running)
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 3
else
    echo "Ollama is already running."
fi

# Pull only qwen3:0.6b model
echo "Pulling model: qwen3:0.6b"
ollama pull "qwen3:0.6b"

# Launch the Streamlit app
if [ -f "app.py" ]; then
    echo "Launching Streamlit app..."
    streamlit run app.py
else
    echo "app.py not found!"
    exit 1
fi
