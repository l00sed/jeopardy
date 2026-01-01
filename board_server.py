#!/usr/bin/env python3
"""
Simple HTTP server for generating random Jeopardy boards on demand.

Usage: python board_server.py
Then open http://localhost:8000 in your browser.
"""

import json
import random
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

# Import the board generator functions
from random_board_generator import load_archive, generate_board

# Global cache for archive data (load once, reuse for all requests)
ARCHIVE_DATA = None


def load_archive_cached():
    """Load archive data once and cache it."""
    global ARCHIVE_DATA
    if ARCHIVE_DATA is None:
        print("Loading archive data (this may take a moment)...")
        ARCHIVE_DATA = load_archive('jeopardy_questions_archive.json')
        print(f"Loaded {len(ARCHIVE_DATA)} questions.")
    return ARCHIVE_DATA


class JeopardyBoardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler that generates random boards on demand."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        # Check if this is a request for a random board
        if parsed_path.path == '/api/generate-board':
            self.generate_random_board(parsed_path)
        else:
            # Serve static files normally
            super().do_GET()
    
    def generate_random_board(self, parsed_path):
        """Generate a new random board and return it as JSON."""
        try:
            # Parse query parameters
            query_params = parse_qs(parsed_path.query)
            difficulty = query_params.get('difficulty', ['medium'])[0]
            
            # Validate difficulty
            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'
            
            # Use a new random seed based on current time
            seed = int(time.time() * 1000000) % (2**32)
            random.seed(seed)
            
            # Load archive and generate board
            archive = load_archive_cached()
            board = generate_board(archive, difficulty)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            # Write board as JSON
            board_json = json.dumps(board, indent=4, ensure_ascii=False)
            self.wfile.write(board_json.encode('utf-8'))
            
            print(f"Generated {difficulty} board (seed: {seed})")
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({
                'error': str(e),
                'message': 'Failed to generate board'
            })
            self.wfile.write(error_response.encode('utf-8'))
            print(f"Error generating board: {e}")
    
    def log_message(self, format, *args):
        """Suppress verbose logging for cleaner output."""
        # Only log board generation, not static file requests
        if 'api/generate-board' in str(args):
            super().log_message(format, *args)


def main():
    """Start the HTTP server."""
    PORT = 8000
    
    print("=" * 60)
    print("Jeopardy Board Server")
    print("=" * 60)
    print()
    print(f"Starting server on http://localhost:{PORT}")
    print(f"Press Ctrl+C to stop the server")
    print()
    print("To play Jeopardy:")
    print(f"  1. Open http://localhost:{PORT} in your browser")
    print("  2. Click 'Generate Random Board'")
    print("  3. Select your difficulty and play!")
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Create and start server
    server = HTTPServer(('localhost', PORT), JeopardyBoardHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()


if __name__ == '__main__':
    main()
