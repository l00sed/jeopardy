#!/bin/bash
# Setup script for semantic search functionality

echo "=================================="
echo "Setting up semantic search..."
echo "=================================="
echo ""

# Check Python version
echo "1. Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is required but not found!"
    exit 1
fi
echo "✓ Python 3 found"
echo ""

# Install dependencies
echo "2. Installing Python dependencies..."
echo "   (This may take a few minutes on first run)"
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Generate embeddings
echo "3. Generating embeddings for all categories..."
echo "   (This will download the ML model on first run - about 80MB)"
python3 generate_embeddings.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate embeddings"
    exit 1
fi
echo "✓ Embeddings generated"
echo ""

echo "=================================="
echo "✓ Setup complete!"
echo "=================================="
echo ""
echo "You can now start the server with:"
echo "  python3 server.py"
echo ""
echo "Then open: http://localhost:8000/creator/"
echo ""
