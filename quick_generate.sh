#!/bin/bash
# Quick start script for generating a random Jeopardy board

cat << "EOF"
  
   _____ ________  ____  ___    ____  ______  __
  / / _ /_  __/ / / / _ \/ _ \  / __ \/ __ \ \/ /
 / / __ |/ / / /_/ / ___/ // / / /_/ / /_/ /\  / 
/_/_/ |_/_/  \____/_/  /____/  \____/\____/ /_/  
                                                  
Random Board Generator

EOF

echo "Quick Start:"
echo ""
echo "1. Generate a single board:"
echo "   ./quick_generate.sh easy"
echo "   ./quick_generate.sh medium"
echo "   ./quick_generate.sh hard"
echo ""
echo "2. Generate all boards:"
echo "   ./generate_all_boards.sh"
echo ""
echo "3. Custom generation:"
echo "   python3 random_board_generator.py --difficulty medium --output boards/my_board.json"
echo ""

# If argument provided, generate that difficulty
if [ "$1" ]; then
    DIFFICULTY=$1
    if [ "$DIFFICULTY" != "easy" ] && [ "$DIFFICULTY" != "medium" ] && [ "$DIFFICULTY" != "hard" ]; then
        echo "❌ Invalid difficulty. Use: easy, medium, or hard"
        exit 1
    fi
    
    echo "Generating $DIFFICULTY board..."
    python3 random_board_generator.py --difficulty $DIFFICULTY --output boards/board_random_$DIFFICULTY.json
    echo ""
    echo "✅ Done! Board saved to: boards/board_random_$DIFFICULTY.json"
    echo ""
    echo "Now open index.html and click 'Generate Random Board'"
else
    echo "Usage: ./quick_generate.sh [easy|medium|hard]"
    echo ""
    echo "Or just run the script to see this help message!"
fi
