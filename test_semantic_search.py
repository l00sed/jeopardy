#!/usr/bin/env python3
"""
Test script to demonstrate semantic search capabilities
"""

import requests
import json

def test_search(query, top_k=5):
    """Test semantic search with a query"""
    url = f"http://localhost:8000/api/search-categories?q={query}&top_k={top_k}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n{'='*60}")
        print(f"Query: '{data['query']}'")
        print(f"Found {data['count']} results:")
        print(f"{'='*60}\n")
        
        for i, result in enumerate(data['results'], 1):
            similarity = result['similarity'] * 100
            print(f"{i}. {result['name']}")
            print(f"   Match: {similarity:.0f}%")
            print(f"   Round: {result['round']}")
            print(f"   Questions: {len(result['questions'])}")
            print()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    # Test various queries to demonstrate semantic understanding
    test_queries = [
        "holidays",
        "celebrations", 
        "festivals",
        "geography",
        "places",
        "locations"
    ]
    
    for query in test_queries:
        test_search(query, top_k=3)
