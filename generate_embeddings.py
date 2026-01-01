#!/usr/bin/env python3
"""
Generate embeddings for all Jeopardy categories to enable semantic search.
This script pre-computes embeddings and saves them for fast lookup.
"""

import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from collections import defaultdict

def generate_embeddings():
    """Generate embeddings for all categories in the historical questions file."""
    
    print("Loading historical questions from full archive...")
    with open('jeopardy_questions_archive.json', 'r') as f:
        questions = json.load(f)
    
    print(f"Loaded {len(questions)} questions")
    
    # Group questions by category and round
    print("Grouping questions by category...")
    category_map = defaultdict(lambda: {'questions': [], 'round': None})
    
    for q in questions:
        category_name = q.get('category', '').strip()
        if not category_name:
            continue
            
        # Clean up the round name
        round_name = q.get('round', '').lower()
        if 'jeopardy!' in round_name and 'double' not in round_name:
            round_name = 'jeopardy'
        elif 'double' in round_name:
            round_name = 'double-jeopardy'
        elif 'final' in round_name:
            round_name = 'final-jeopardy'
        else:
            round_name = 'jeopardy'  # default
        
        category_map[category_name]['questions'].append({
            'question': q.get('question', ''),
            'answer': q.get('answer', ''),
            'value': str(q.get('value') or '$200').replace('$', '').replace(',', ''),
            'air_date': q.get('air_date', ''),
            'show_number': q.get('show_number', '')
        })
        
        # Set round if not set, or use the most common round for this category
        if category_map[category_name]['round'] is None:
            category_map[category_name]['round'] = round_name
    
    print(f"Found {len(category_map)} unique categories")
    
    print("Loading embedding model (this may take a moment on first run)...")
    # Using a lightweight but effective model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Collect all categories with their context
    categories = []
    
    print("Processing categories and creating embeddings text...")
    
    for category_name, data in category_map.items():
        # Create rich text for embedding: category name + question text
        text_for_embedding = category_name
        
        # Add question text for better semantic context (first 3 questions)
        if data['questions']:
            question_texts = [q.get('question', '') for q in data['questions'][:3] if q.get('question')]
            if question_texts:
                text_for_embedding += " " + " ".join(question_texts)
        
        categories.append({
            'name': category_name,
            'questions': data['questions'][:5],  # Keep only first 5 questions for display
            'round': data['round'],
            'text': text_for_embedding,
            'total_questions': len(data['questions'])
        })
    
    print(f"Generating embeddings for {len(categories)} categories...")
    
    # Generate embeddings in batch for efficiency
    texts = [cat['text'] for cat in categories]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Save the data
    output_data = {
        'categories': categories,
        'embeddings': embeddings,
        'model_name': 'all-MiniLM-L6-v2'
    }
    
    print("Saving embeddings to file...")
    with open('category_embeddings.pkl', 'wb') as f:
        pickle.dump(output_data, f)
    
    print(f"✓ Successfully generated embeddings for {len(categories)} categories")
    print(f"✓ Saved to category_embeddings.pkl")
    print(f"✓ Embedding dimension: {embeddings.shape[1]}")

if __name__ == '__main__':
    generate_embeddings()
