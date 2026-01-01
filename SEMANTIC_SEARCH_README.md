# Semantic Search Feature for Jeopardy Board Creator

## Overview

The board creator now includes semantic search powered by machine learning embeddings. This allows you to find relevant categories even when they don't contain your exact search terms.

## How It Works

Instead of simple keyword matching, the search understands the **meaning** of your query and finds categories that are semantically similar.

### Examples

- Searching for "presidents" will find categories like:
  - "COMMANDER IN CHIEF"
  - "THE WHITE HOUSE"
  - "AMERICAN LEADERS"
  - "OVAL OFFICE"

- Searching for "space" will find:
  - "ASTRONOMY"
  - "NASA"
  - "THE SOLAR SYSTEM"
  - "ROCKETS"

## Setup

1. **Install dependencies:**
   ```bash
   ./setup_semantic_search.sh
   ```

   Or manually:
   ```bash
   pip3 install -r requirements.txt
   python3 generate_embeddings.py
   ```

2. **Start the server:**
   ```bash
   python3 server.py
   ```

3. **Open the creator:**
   Navigate to `http://localhost:8000/creator/`

## Usage

1. Type your search term in the "Search for categories" field
2. Results appear ranked by similarity (with percentage match)
3. Click "Import to Jeopardy" or "Import to Double Jeopardy" to add the category to your board

## Technical Details

- **Model:** `all-MiniLM-L6-v2` (lightweight, 384-dimensional embeddings)
- **Search Method:** Cosine similarity between query and category embeddings
- **Context:** Category names + first 3 questions for better semantic understanding
- **Fallback:** If the API fails, falls back to keyword search

## Files

- `generate_embeddings.py` - Pre-computes embeddings for all categories
- `category_embeddings.pkl` - Cached embeddings (generated automatically)
- `server.py` - Includes `/api/search-categories` endpoint
- `requirements.txt` - Python dependencies
- `setup_semantic_search.sh` - One-command setup script

## Performance

- First-time setup: ~2-3 minutes (downloads model, generates embeddings)
- Subsequent searches: Near-instant (embeddings are cached)
- Model size: ~80MB

## Troubleshooting

If semantic search fails, the system will automatically fall back to keyword search. Check the browser console for error messages.

To regenerate embeddings:
```bash
python3 generate_embeddings.py
```
