#!/usr/bin/env python3
"""
Simple HTTP server for Jeopardy game that can generate random boards on-demand.
This allows the "Generate Random Board" button to actually generate new boards.
"""

import http.server
import socketserver
import json
import subprocess
import os
import pickle
import numpy as np
from urllib.parse import urlparse, parse_qs

PORT = 8000

# Global variable to store embeddings data
EMBEDDINGS_DATA = None

class JeopardyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Handle the generate board API endpoint
        if parsed_path.path == '/api/generate-board':
            self.handle_generate_board()
        # Handle the semantic search API endpoint
        elif parsed_path.path == '/api/search-categories':
            self.handle_search_categories()
        else:
            # Serve static files normally
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        
        # Handle the save board API endpoint
        if parsed_path.path == '/api/save-board':
            self.handle_save_board()
        else:
            self.send_error_response(404, 'Not found')
    
    def handle_generate_board(self):
        """Generate a new random board using the Python script."""
        try:
            # Parse query parameters
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            difficulty = params.get('difficulty', ['medium'])[0]
            
            # Validate difficulty
            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'
            
            output_file = f'boards/board_random_{difficulty}.json'
            
            print(f"Generating {difficulty} board...")
            
            # Run the random board generator script
            result = subprocess.run(
                ['python3', 'random_board_generator.py', 
                 '--difficulty', difficulty, 
                 '--output', output_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"Board generation failed: {result.stderr}")
            
            print(f"✓ Generated {difficulty} board successfully")
            
            # Read the generated board file
            with open(output_file, 'r', encoding='utf-8') as f:
                board_data = json.load(f)
            
            # Send success response with the board data
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'message': f'Generated {difficulty} board',
                'board': board_data
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except subprocess.TimeoutExpired:
            self.send_error_response(500, 'Board generation timed out')
        except Exception as e:
            print(f"Error generating board: {e}")
            self.send_error_response(500, str(e))
    
    def send_error_response(self, code, message):
        """Send an error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': False,
            'error': message
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_search_categories(self):
        """Handle semantic search for categories."""
        global EMBEDDINGS_DATA
        
        try:
            # Parse query parameters
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            query = params.get('q', [''])[0]
            top_k = int(params.get('top_k', ['20'])[0])
            
            if not query:
                self.send_error_response(400, 'Query parameter "q" is required')
                return
            
            # Load embeddings if not already loaded
            if EMBEDDINGS_DATA is None:
                print("Loading embeddings...")
                if not os.path.exists('category_embeddings.pkl'):
                    self.send_error_response(500, 'Embeddings file not found. Please run generate_embeddings.py first.')
                    return
                
                with open('category_embeddings.pkl', 'rb') as f:
                    EMBEDDINGS_DATA = pickle.load(f)
                
                # Also load the model for encoding queries
                from sentence_transformers import SentenceTransformer
                EMBEDDINGS_DATA['model'] = SentenceTransformer(EMBEDDINGS_DATA['model_name'])
                print(f"✓ Loaded embeddings for {len(EMBEDDINGS_DATA['categories'])} categories")
            
            # Encode the query
            query_embedding = EMBEDDINGS_DATA['model'].encode([query])[0]
            
            # Compute cosine similarity
            embeddings = EMBEDDINGS_DATA['embeddings']
            similarities = np.dot(embeddings, query_embedding) / (
                np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                category = EMBEDDINGS_DATA['categories'][idx]
                results.append({
                    'name': category['name'],
                    'questions': category['questions'],
                    'round': category['round'],
                    'similarity': float(similarities[idx])
                })
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            import traceback
            traceback.print_exc()
            self.send_error_response(500, str(e))
    
    def handle_save_board(self):
        """Handle saving a board to the boards directory."""
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Get filename and board data
            filename = data.get('filename', 'board_custom')
            board = data.get('board')
            
            if not board:
                self.send_error_response(400, 'Board data is required')
                return
            
            # Sanitize filename (remove any path traversal attempts)
            filename = os.path.basename(filename)
            # Remove .json extension if present
            if filename.endswith('.json'):
                filename = filename[:-5]
            
            # Create boards directory if it doesn't exist
            boards_dir = 'boards'
            if not os.path.exists(boards_dir):
                os.makedirs(boards_dir)
            
            # Full filepath
            filepath = os.path.join(boards_dir, f'{filename}.json')
            
            # Save the board
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(board, f, indent=4, ensure_ascii=False)
            
            print(f"✓ Saved board to: {filepath}")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'Board saved successfully',
                'filepath': filepath
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error saving board: {e}")
            import traceback
            traceback.print_exc()
            self.send_error_response(500, str(e))
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        if args[1] != '304':  # Don't log 304 (Not Modified) responses
            super().log_message(format, *args)


def main():
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), JeopardyHandler) as httpd:
        print(f"\n{'='*60}")
        print(f"  🎮 Jeopardy Game Server Running!")
        print(f"{'='*60}")
        print(f"\n  Server address: http://localhost:{PORT}")
        print(f"\n  Open your browser to: http://localhost:{PORT}/index.html")
        print(f"\n  Press Ctrl+C to stop the server")
        print(f"\n{'='*60}\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n  Server stopped.")
            print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
