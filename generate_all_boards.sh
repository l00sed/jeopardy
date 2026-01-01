#!/bin/bash
# generate_all_boards.sh
# Generates random boards for all difficulty levels

echo "========================================="
echo "  Jeopardy Random Board Generator"
echo "========================================="
echo ""
echo "Generating boards for all difficulty levels..."
echo ""

# Generate easy board
echo "📝 Generating EASY board..."
python3 random_board_generator.py --difficulty easy --output boards/board_random_easy.json
echo ""

# Generate medium board
echo "📝 Generating MEDIUM board..."
python3 random_board_generator.py --difficulty medium --output boards/board_random_medium.json
echo ""

# Generate hard board
echo "📝 Generating HARD board..."
python3 random_board_generator.py --difficulty hard --output boards/board_random_hard.json
echo ""

# Generate default board (medium)
echo "📝 Generating DEFAULT board (medium)..."
python3 random_board_generator.py --difficulty medium --output boards/board_random.json
echo ""

echo "========================================="
echo "✅ All boards generated successfully!"
echo "========================================="
echo ""
echo "Generated files:"
echo "  - boards/board_random_easy.json"
echo "  - boards/board_random_medium.json"
echo "  - boards/board_random_hard.json"
echo "  - boards/board_random.json (default)"
echo ""
echo "You can now open index.html and use the"
echo "'Generate Random Board' feature!"
echo ""
