#!/bin/bash

# Sage Setup Script
# Installs all dependencies. The app UI handles backend choice.

echo "🌿 Setting up Sage..."
echo ""

# Ensure Homebrew is in PATH (for Apple Silicon and Intel Macs)
if [ -f "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f "/usr/local/bin/brew" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install it first:"
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install streamlit anthropic requests sentence-transformers chromadb --quiet
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Build RAG index
echo "🔍 Building knowledge base index..."
cd "$(dirname "$0")"
python3 -c "from rag import index_knowledge_base; n = index_knowledge_base(force=True); print(f'✅ Indexed {n} chunks')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  RAG index build skipped (will build on first use)"
fi

# Install Homebrew if needed (for Ollama option)
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

if command -v brew &> /dev/null; then
    echo "✅ Homebrew ready"
    
    # Install Ollama
    if ! command -v ollama &> /dev/null; then
        echo "📦 Installing Ollama..."
        brew install ollama
    fi
    
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama installed"
        
        # Start Ollama server in background
        echo "🚀 Starting Ollama server..."
        ollama serve &>/dev/null &
        OLLAMA_PID=$!
        sleep 3  # Give it time to start
        
        # Pull the model
        if ! ollama list 2>/dev/null | grep -q "llama3.1:8b"; then
            echo "📥 Downloading Llama 3.1 model (~4GB, one-time)..."
            ollama pull llama3.1:8b
        fi
        
        if ollama list 2>/dev/null | grep -q "llama3.1:8b"; then
            echo "✅ Llama model ready"
        else
            echo "⚠️  Model download may have failed - you can retry in the app"
        fi
        
        # Stop the background server (user will start it when needed)
        kill $OLLAMA_PID 2>/dev/null
    fi
else
    echo "⚠️  Homebrew not available - Ollama option won't work"
    echo "   Claude API will still work fine"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "To run PM Saboteurs:"
echo ""
echo "  bash run.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
