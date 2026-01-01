#!/usr/bin/env python3
"""
Random Jeopardy Board Generator

Generates a random Jeopardy board from the archive dataset with difficulty filtering.
Usage: python random_board_generator.py --difficulty easy|medium|hard [--output filename.json]
"""

import json
import random
import argparse
from collections import defaultdict

# Try to import ftfy, use fallback if not available
try:
    from ftfy import fix_text
except ImportError:
    print("Warning: ftfy module not found. Using simple text cleanup instead.")
    print("To install ftfy: pip install ftfy")
    def fix_text(text):
        """Fallback function if ftfy is not available."""
        if text is None:
            return ""
        # Basic cleanup - decode unicode escapes and strip whitespace
        return text.strip()


# Difficulty level value ranges (in dollars)
DIFFICULTY_RANGES = {
    'easy': {
        'jeopardy': [100, 200, 300, 400, 500],
        'double-jeopardy': [200, 400, 600, 800, 1000],
        'description': 'Easier questions from early rounds'
    },
    'medium': {
        'jeopardy': [200, 400, 600, 800, 1000],
        'double-jeopardy': [400, 800, 1200, 1600, 2000],
        'description': 'Standard difficulty questions'
    },
    'hard': {
        'jeopardy': [400, 600, 800, 1000, 1200],
        'double-jeopardy': [800, 1200, 1600, 2000],
        'description': 'Harder questions from later rounds'
    }
}


def load_archive(filepath='jeopardy_questions_archive.json'):
    """Load the Jeopardy questions archive."""
    print(f"Loading archive from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} questions from archive.")
    return data


def organize_by_category(archive_data):
    """Organize questions by category and round."""
    by_category = defaultdict(lambda: defaultdict(list))
    
    for question in archive_data:
        if not all(k in question for k in ['category', 'round', 'value', 'question', 'answer']):
            continue
        
        category = question['category']
        round_name = question['round']
        
        # Skip Final Jeopardy for now (we'll handle separately)
        if 'Final' in round_name:
            continue
            
        by_category[category][round_name].append(question)
    
    return by_category


def get_value_from_string(value_str):
    """Extract numeric value from string like '$200'."""
    try:
        return int(value_str.strip('$').replace(',', ''))
    except (ValueError, AttributeError):
        return 0


def select_unique_questions_for_category(questions, target_values):
    """
    Select UNIQUE questions matching target values for a category.
    Ensures no duplicate questions and proper value sequence.
    Returns list of selected questions or None if not enough unique questions available.
    """
    selected = []
    used_questions = set()  # Track question text to avoid duplicates
    
    for target_value in target_values:
        # Find questions with matching value that haven't been used
        matching = [
            q for q in questions 
            if get_value_from_string(q['value']) == target_value 
            and q['question'] not in used_questions
        ]
        
        if matching:
            chosen = random.choice(matching)
            selected.append(chosen)
            used_questions.add(chosen['question'])
        else:
            # If exact value not found or all used, try to find closest unused value
            unused = [q for q in questions if q['question'] not in used_questions]
            if unused:
                closest = min(unused, key=lambda q: abs(get_value_from_string(q['value']) - target_value))
                selected.append(closest)
                used_questions.add(closest['question'])
            else:
                # Not enough unique questions in this category
                return None
    
    # Verify we got the right number of unique questions
    if len(selected) != len(target_values):
        return None
    
    # Double-check for duplicates
    question_texts = [q['question'] for q in selected]
    if len(question_texts) != len(set(question_texts)):
        return None
    
    return selected


def select_categories_for_round(by_category, round_name, target_values, num_categories=6):
    """
    Select random categories with enough UNIQUE questions for a round.
    Uses a seed based on current time to ensure different results each run.
    """
    # Filter categories that have enough unique questions in this round
    viable_categories = []
    
    for cat, rounds in by_category.items():
        if round_name not in rounds:
            continue
        
        questions = rounds[round_name]
        
        # Check if category has enough unique questions
        unique_questions = len(set(q['question'] for q in questions))
        
        # Need at least 5 unique questions for a proper category
        if unique_questions >= 5 and len(questions) >= len(target_values):
            viable_categories.append(cat)
    
    if len(viable_categories) < num_categories:
        print(f"Warning: Only {len(viable_categories)} viable categories available for {round_name}")
        num_categories = min(num_categories, len(viable_categories))
    
    # Randomly select categories (this will be different each run due to random.choice)
    selected_categories = random.sample(viable_categories, num_categories)
    
    round_data = []
    for category in selected_categories:
        questions = by_category[category][round_name]
        selected_questions = select_unique_questions_for_category(questions, target_values)
        
        if selected_questions:
            category_obj = {
                "name": fix_text(category.upper()),
                "questions": []
            }
            
            # Sort selected questions by their assigned target value to ensure proper ordering
            for i, q in enumerate(selected_questions):
                question_obj = {
                    "value": target_values[i],  # Use the target value for consistency
                    "question": fix_text(q['question'].upper()),
                    "answer": fix_text(q['answer'])
                }
                
                # Preserve image if present
                if 'image' in q and q['image']:
                    question_obj['image'] = q['image']
                
                category_obj["questions"].append(question_obj)
            
            round_data.append(category_obj)
    
    return round_data


def add_daily_doubles(round_data, num_doubles, min_value_index=2):
    """Add daily double flags to random questions (avoiding first two rows)."""
    # Get all valid question positions (category, question_index)
    valid_positions = []
    for cat_idx, category in enumerate(round_data):
        for q_idx in range(min_value_index, len(category['questions'])):
            valid_positions.append((cat_idx, q_idx))
    
    if len(valid_positions) < num_doubles:
        num_doubles = len(valid_positions)
    
    # Randomly select positions for daily doubles
    dd_positions = random.sample(valid_positions, num_doubles)
    
    for cat_idx, q_idx in dd_positions:
        round_data[cat_idx]['questions'][q_idx]['daily-double'] = "true"
    
    return round_data


def select_final_jeopardy(archive_data):
    """Select a random Final Jeopardy question."""
    final_questions = [q for q in archive_data 
                      if 'round' in q and 'Final' in q['round']
                      and 'category' in q and 'question' in q and 'answer' in q]
    
    if not final_questions:
        return {
            "category": "RANDOM TRIVIA",
            "question": "THIS IS A PLACEHOLDER FINAL JEOPARDY QUESTION",
            "answer": "What is a placeholder answer?"
        }
    
    selected = random.choice(final_questions)
    final_obj = {
        "category": fix_text(selected['category'].upper()),
        "question": fix_text(selected['question'].upper()),
        "answer": fix_text(selected['answer'])
    }
    
    # Preserve image if present
    if 'image' in selected and selected['image']:
        final_obj['image'] = selected['image']
    
    return final_obj


def generate_board(archive_data, difficulty='medium'):
    """Generate a complete Jeopardy board with specified difficulty."""
    if difficulty not in DIFFICULTY_RANGES:
        raise ValueError(f"Invalid difficulty. Choose from: {', '.join(DIFFICULTY_RANGES.keys())}")
    
    print(f"\nGenerating {difficulty} difficulty board...")
    print(f"Description: {DIFFICULTY_RANGES[difficulty]['description']}")
    
    # Organize questions by category
    by_category = organize_by_category(archive_data)
    
    # Generate Jeopardy round
    print("\nGenerating Jeopardy round...")
    jeopardy_values = DIFFICULTY_RANGES[difficulty]['jeopardy']
    jeopardy_round = select_categories_for_round(
        by_category, 'Jeopardy!', jeopardy_values, num_categories=6
    )
    jeopardy_round = add_daily_doubles(jeopardy_round, num_doubles=1, min_value_index=2)
    print(f"Selected {len(jeopardy_round)} categories with unique questions")
    
    # Generate Double Jeopardy round
    print("\nGenerating Double Jeopardy round...")
    double_jeopardy_values = DIFFICULTY_RANGES[difficulty]['double-jeopardy']
    double_jeopardy_round = select_categories_for_round(
        by_category, 'Double Jeopardy!', double_jeopardy_values, num_categories=6
    )
    double_jeopardy_round = add_daily_doubles(double_jeopardy_round, num_doubles=2, min_value_index=2)
    print(f"Selected {len(double_jeopardy_round)} categories with unique questions")
    
    # Generate Final Jeopardy
    print("\nGenerating Final Jeopardy...")
    final_jeopardy = select_final_jeopardy(archive_data)
    print(f"Category: {final_jeopardy['category']}")
    
    # Assemble board
    board = {
        "jeopardy": jeopardy_round,
        "double-jeopardy": double_jeopardy_round,
        "final-jeopardy": final_jeopardy
    }
    
    return board


def main():
    parser = argparse.ArgumentParser(
        description='Generate a random Jeopardy board from the archive dataset'
    )
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'medium', 'hard'],
        default='medium',
        help='Difficulty level for questions (default: medium)'
    )
    parser.add_argument(
        '--output',
        default='boards/board_random.json',
        help='Output filename (default: boards/board_random.json)'
    )
    parser.add_argument(
        '--archive',
        default='jeopardy_questions_archive.json',
        help='Path to archive file (default: jeopardy_questions_archive.json)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducible boards (default: None for truly random)'
    )
    
    args = parser.parse_args()
    
    # Set random seed if provided, otherwise use system time for true randomness
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    else:
        # Explicitly use system time to ensure different results each run
        import time
        seed = int(time.time() * 1000000) % (2**32)
        random.seed(seed)
        print(f"Using random seed: {seed} (auto-generated)")
    
    # Load archive
    archive_data = load_archive(args.archive)
    
    # Generate board
    board = generate_board(archive_data, args.difficulty)
    
    # Save to file
    print(f"\nSaving board to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(board, f, indent=4, ensure_ascii=False)
    
    print(f"\n✓ Successfully generated {args.difficulty} difficulty board!")
    print(f"  Output: {args.output}")
    print(f"  Jeopardy Round: {len(board['jeopardy'])} categories")
    print(f"  Double Jeopardy Round: {len(board['double-jeopardy'])} categories")
    print(f"  Final Jeopardy: {board['final-jeopardy']['category']}")
    print("\nYou can now load this board in the Jeopardy game!")


if __name__ == '__main__':
    main()
