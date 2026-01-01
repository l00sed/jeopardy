#!/bin/bash
# Quick start script for the Jeopardy Board Server

echo "Starting Jeopardy Board Server..."
echo ""
echo "This will start a local web server that generates random Jeopardy boards."
echo "Press Ctrl+C to stop the server when you're done playing."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Start the server
python3 board_server.py
