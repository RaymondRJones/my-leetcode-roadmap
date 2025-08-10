#!/bin/bash

# LeetCode Roadmap Generator Startup Script

echo "🚀 Starting LeetCode Roadmap Generator..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q pdfplumber flask pandas

# Check for PDF files
pdf_count=$(ls *.pdf 2>/dev/null | wc -l)
if [ $pdf_count -eq 0 ]; then
    echo "⚠️  No PDF files found in current directory"
    echo "   Please add your LeetCode roadmap PDF files to this directory"
else
    echo "📄 Found $pdf_count PDF files"
fi

# Parse PDFs and generate roadmap data
echo "🔍 Analyzing PDF files and generating roadmap..."
python pdf_analyzer.py

# Start the web application
echo ""
echo "🌐 Starting web server..."
echo "   The server will automatically find an available port"
echo "   Press Ctrl+C to stop the server"
echo ""
python app.py