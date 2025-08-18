#!/bin/bash

# AI Resume Generator Setup Script with Anthropic Claude
# This script sets up the environment and installs dependencies

echo "🚀 Setting up AI Resume Generator with Anthropic Claude"
echo "=" * 60

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [ ! "$python_version" ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $python_version found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "🔑 Please edit the .env file and add your Anthropic API key:"
    echo "   ANTHROPIC_API_KEY=your_anthropic_api_key_here"
    echo ""
    echo "   You can get your API key from: https://console.anthropic.com/"
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "🔥 Next steps:"
echo "1. Edit .env file and add your Anthropic API key"
echo "2. Run tests: python test_anthropic.py"
echo "3. Run Phase 1 tests: python -m pytest tests/test_phase1.py -v"
echo "4. Start the API server: uvicorn app.main:app --reload"
echo ""
echo "💡 Don't forget to activate the virtual environment:"
echo "   source .venv/bin/activate"
