#!/bin/bash
# ============================================
# YouTube Q&A Genius - Quick Setup Script
# ============================================

echo ""
echo "🎯 YouTube Q&A Genius - Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✅ Python: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo ""
echo "📥 Installing dependencies (this may take 2-3 minutes)..."
pip install -r requirements.txt -q

echo ""
echo "✅ Dependencies installed!"

# Setup .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "📝 Created .env file from template"
    echo "⚠️  IMPORTANT: Edit .env and add your API key!"
    echo ""
    echo "   Get FREE Groq API key at: https://console.groq.com"
    echo "   Then edit .env: GROQ_API_KEY=your_key_here"
fi

echo ""
echo "🚀 Setup complete! To run the app:"
echo ""
echo "   source venv/bin/activate"
echo "   streamlit run app.py"
echo ""
echo "   Then open: http://localhost:8501"
echo ""