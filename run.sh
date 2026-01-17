#!/bin/bash

# PM Saboteurs Run Script
# Just double-click or run: ./run.sh

cd "$(dirname "$0")"

# Start Ollama in background if installed (for local mode)
if command -v ollama &> /dev/null; then
    echo "🦙 Starting Ollama in background..."
    ollama serve &> /dev/null &
    sleep 2
fi

# Run the app
python3 -m streamlit run app.py
